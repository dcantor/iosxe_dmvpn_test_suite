*** Settings ***
Documentation     Pushing configuration to the devices with Terraform.
...
...               The question this suite answers is narrow and practical: can a
...               change written as Terraform reach these routers, does Terraform
...               then agree with what is on them, and can it take back what it
...               put there.
...
...               Every check that something landed is made over the CLI, not
...               through the RESTCONF API that performed the write. An API
...               reporting its own success proves only that the API is
...               self-consistent; the device's running configuration is the
...               thing that decides.
...
...               Terraform owns Loopback99 and the TF-MANAGED access list, and
...               nothing else. Both sit outside the ranges the provisioning
...               phases use, so Terraform and the harness are never editing the
...               same object -- if they were, the loser would surface as an
...               unrelated suite failing intermittently.
Resource          ../resources/c8000v.resource
Library           ${CURDIR}/../tools/terraform_keywords.py
Library           String
Suite Setup       Run Keywords    Open All Routers
...               AND    Generate Terraform Variables
...               AND    Terraform Init
...               AND    Terraform Destroy
Suite Teardown    Run Keywords    Terraform Destroy    AND    Close All Connections

*** Variables ***
${TF_LOOPBACK}    Loopback99
${TF_ACL}         TF-MANAGED
${HAND_EDIT}      Changed by hand

*** Test Cases ***
The Terraform Configuration Is Valid And Canonically Formatted
    [Documentation]    The cheapest gate there is, and the one most worth having
    ...                first: a syntax or type error here would otherwise surface
    ...                as a confusing failure several tests later.
    Terraform Validate
    Terraform Formatting Is Canonical

A Plan From An Empty State Proposes Every Managed Resource
    [Documentation]    Two resources on each of three routers. Asserting the count
    ...                catches a provider that silently drops a device from the
    ...                loop — a plan that proposes four resources instead of six
    ...                still looks like success in the summary line.
    ${out}=    Plan Should Propose Changes
    Should Contain    ${out}    6 to add
    ...    Terraform did not propose one loopback and one access list per router:\n${out}

Apply Puts The Loopback On Every Router
    [Documentation]    The push itself, read back from the running configuration.
    Terraform Apply
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config interface ${TF_LOOPBACK}
        Should Contain    ${cfg}    description Managed by Terraform
        ...    ${r} has no Terraform-managed description on ${TF_LOOPBACK}
        Should Contain    ${cfg}    255.255.255.255
        ...    ${r} did not receive the /32 mask Terraform specified
    END

Each Router Receives Its Own Address, Not A Shared One
    [Documentation]    A per-device value has to survive the provider's device
    ...                loop. If it does not, every router ends up with the first
    ...                one's address — which still passes a test that only checks
    ...                "an address is configured".
    ${expected}=    Terraform Output    loopbacks
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config interface ${TF_LOOPBACK}
        Should Contain    ${cfg}    ip address ${expected}[${r}][address]
        ...    ${r} does not carry the address Terraform recorded for it
    END

The Access List Arrives With Its Entries In Order
    [Documentation]    An ordered list is where a provider and a device are most
    ...                likely to disagree. Sequence numbers make the order
    ...                explicit, so it can be asserted rather than assumed.
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config | section ip access-list standard ${TF_ACL}
        Should Contain    ${cfg}    10 remark Managed by Terraform
        Should Contain    ${cfg}    20 permit 10.99.0.0 0.0.255.255
        Should Contain    ${cfg}    30 deny any
        ${ten}=      Get Index Of Substring    ${cfg}    10 remark
        ${twenty}=   Get Index Of Substring    ${cfg}    20 permit
        ${thirty}=   Get Index Of Substring    ${cfg}    30 deny
        Should Be True    ${ten} < ${twenty} < ${thirty}
        ...    ${r} holds the access list entries out of order
    END

Applying The Same Configuration Twice Proposes Nothing
    [Documentation]    Idempotence, and the sharpest single check in this suite.
    ...                A provider that cannot read back what it wrote reports a
    ...                permanent difference here, which would mean every future
    ...                plan is noisy and real drift becomes invisible in it.
    Plan Should Be Clean

A Change Made By Hand Is Reported As Drift
    [Documentation]    The reason to keep configuration in Terraform at all. The
    ...                device is edited from the CLI behind Terraform's back, and
    ...                the next plan has to notice.
    ...
    ...                The wait is not padding. A change made at the CLI is not
    ...                immediately visible over RESTCONF: measured on this
    ...                platform, a plan run in the same second reports no drift,
    ...                and the same plan two seconds later reports it. Polling
    ...                until the plan sees it keeps the test honest about what is
    ...                being asserted -- that the drift is detected at all, not
    ...                that it is detected instantly.
    ...
    ...                It is also worth knowing beyond this test: any tool that
    ...                writes at the CLI and verifies over RESTCONF can read its
    ...                own change back as absent.
    [Teardown]    Terraform Apply
    Configure On    R2    interface ${TF_LOOPBACK}    description ${HAND_EDIT}
    ${out}=    Wait Until Keyword Succeeds    10x    2s    Plan Should Propose Changes
    Should Contain    ${out}    ${HAND_EDIT}
    ...    the plan proposes changes but does not name the hand edit, so it may
    ...    be reacting to something else entirely:\n${out}
    Should Contain    ${out}    1 to change
    ...    drift on one attribute of one device did not produce exactly one change

Applying Puts A Hand-Edited Device Back
    [Documentation]    Detection is only half of it; the correction is what makes
    ...                the declared state authoritative.
    ${cfg}=    Run On    R2    show running-config interface ${TF_LOOPBACK}
    Should Contain    ${cfg}    description Managed by Terraform
    ...    R2 was not returned to the state Terraform declares
    Should Not Contain    ${cfg}    ${HAND_EDIT}
    ...    the hand edit survived an apply
    Plan Should Be Clean

Destroy Removes Everything Terraform Created
    [Documentation]    Taking it back matters as much as putting it there: a lab
    ...                that cannot be returned to a known state stops being a lab.
    Terraform Destroy
    FOR    ${r}    IN    @{ROUTERS}
        ${lo}=    Run On    ${r}    show running-config interface ${TF_LOOPBACK}
        Should Not Contain    ${lo}    Managed by Terraform
        ...    ${r} still carries the Terraform loopback after destroy
        ${acl}=    Run On    ${r}    show running-config | include ip access-list standard ${TF_ACL}
        Should Not Contain    ${acl}    ${TF_ACL}
        ...    ${r} still carries the Terraform access list after destroy
    END
    ${count}=    Terraform State Resource Count
    Should Be Equal As Integers    ${count}    0
    ...    Terraform still holds ${count} resources in state after destroy

*** Keywords ***
Get Index Of Substring
    [Arguments]    ${text}    ${needle}
    ${idx}=    Evaluate    """${text}""".find("""${needle}""")
    Should Be True    ${idx} >= 0    ${needle} is not present at all
    RETURN    ${idx}
