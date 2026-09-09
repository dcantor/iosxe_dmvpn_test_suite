*** Settings ***
Documentation     Pushing configuration with Cisco's Network as Code module.
...
...               The sibling suite writes Terraform resources by hand and talks
...               RESTCONF. This one uses netascode/nac-iosxe, where the
...               configuration is a YAML data model and Terraform is only the
...               engine that renders it. Both end at the same place -- running
...               configuration on three routers -- so the interesting part is
...               where they differ.
...
...               They differ in transport, and not by choice. The module needs
...               the iosxe provider at 1.0.0 or newer, and 1.0.0 removed
...               RESTCONF outright: no protocol attribute, no url attribute,
...               default port 830. Anything built on this module speaks NETCONF.
...
...               As before, every check that configuration landed reads the CLI
...               rather than the API that wrote it.
...
...               Network as Code owns Loopback98 and the NAC-MANAGED access
...               list. The hand-written suite owns Loopback99 and TF-MANAGED.
...               Separate objects, separate state, separate working directories:
...               the two can run in either order without meeting.
Resource          ../resources/c8000v.resource
Library           ${CURDIR}/../tools/nac_keywords.py
Library           Collections
Suite Setup       Run Keywords    Open All Routers
...               AND    Render Nac Model
...               AND    Nac Init
...               AND    Nac Destroy
Suite Teardown    Run Keywords    Nac Destroy    AND    Close All Connections

*** Variables ***
${NAC_LOOPBACK}    Loopback98
${NAC_ACL}         NAC-MANAGED
${NAC_DESC}        Managed by Network as Code
${HAND_EDIT}       Changed by hand

*** Test Cases ***
The Module Resolves Against A NETCONF-Only Provider
    [Documentation]    Recording the constraint rather than discovering it again.
    ...                The module requires iosxe >= 1.0.0; 1.0.0 is NETCONF-only.
    ...                If a later provider restores RESTCONF, or the module
    ...                relaxes its floor, this test is where that shows up --
    ...                and the device host in the model would need revisiting,
    ...                because it points at the forwarded NETCONF port.
    Nac Validate
    ${version}=    Nac Provider Version
    Should Start With    ${version}    1.
    ...    the locked provider is ${version}; this suite's NETCONF assumption was
    ...    written against the 1.x line

The Data Model Carries An Address For Every Router
    [Documentation]    The trap this module sets. Every optional key is read
    ...                through try(), so a key at the wrong nesting depth is not
    ...                an error -- it is dropped in silence. An address written
    ...                at the top of an interface entry instead of under ipv4:
    ...                yields a successful plan that creates a loopback with no
    ...                address on it.
    ...
    ...                So the model is checked for shape before anything is
    ...                pushed, and the address is asserted on the device
    ...                afterwards. Either check alone would have missed it.
    ${model}=    Read Nac Model
    ${devices}=    Set Variable    ${model}[iosxe][devices]
    Length Should Be    ${devices}    3
    ...    the model does not describe all three routers
    FOR    ${d}    IN    @{devices}
        ${loopbacks}=    Set Variable    ${d}[configuration][interfaces][loopbacks]
        Dictionary Should Contain Key    ${loopbacks}[0]    ipv4
        ...    ${d}[name] has a loopback with no ipv4 block, which the module
        ...    would accept and quietly push without an address
        Dictionary Should Contain Key    ${loopbacks}[0][ipv4]    address
    END

Applying The Model Configures Every Router
    [Documentation]    The push itself, read back from running configuration.
    Nac Apply
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config interface ${NAC_LOOPBACK}
        Should Contain    ${cfg}    description ${NAC_DESC}
        ...    ${r} did not receive the Network as Code loopback
    END

The Address From The Model Reaches The Device
    [Documentation]    The half that catches a silently dropped key: not that a
    ...                loopback exists, but that it carries the address the model
    ...                declares for that specific router.
    ${model}=    Read Nac Model
    FOR    ${d}    IN    @{model}[iosxe][devices]
        ${cfg}=    Run On    ${d}[name]    show running-config interface ${NAC_LOOPBACK}
        Should Contain    ${cfg}    ip address ${d}[configuration][interfaces][loopbacks][0][ipv4][address]
        ...    ${d}[name] has the loopback but not the address the model gives it,
        ...    which is what a mis-nested key looks like from the device side
    END

The Abstract Access List Model Renders To Ordered Entries
    [Documentation]    The model says action: permit with a prefix; the device
    ...                gets "20 permit 10.98.0.0 0.0.255.255". This checks the
    ...                translation, and that ordering survives it.
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config | section ip access-list standard ${NAC_ACL}
        Should Contain    ${cfg}    10 remark ${NAC_DESC}
        Should Contain    ${cfg}    20 permit 10.98.0.0 0.0.255.255
        Should Contain    ${cfg}    30 deny any
    END

Rendering The Same Model Twice Proposes Nothing
    [Documentation]    Idempotence across the whole rendering path: YAML to
    ...                model to resources to device, and back again.
    Nac Plan Should Be Clean

A Change Made By Hand Is Reported As Drift
    [Documentation]    Worth comparing with the RESTCONF suite, which has to wait
    ...                for this. Over RESTCONF a plan run in the same second as a
    ...                CLI edit reports no drift and needs about two seconds to
    ...                see it. Over NETCONF the same edit is visible immediately,
    ...                measured at zero delay.
    ...
    ...                That is a property of the transport, not of Terraform, and
    ...                it is asserted here without a wait deliberately: if this
    ...                test ever starts needing one, NETCONF has begun behaving
    ...                like RESTCONF and that is worth being told about.
    [Teardown]    Nac Apply
    Configure On    R2    interface ${NAC_LOOPBACK}    description ${HAND_EDIT}
    ${out}=    Nac Plan Should Propose Changes
    Should Contain    ${out}    ${HAND_EDIT}
    ...    the plan proposes changes but does not name the hand edit:\n${out}

Applying Puts A Hand-Edited Device Back
    ${cfg}=    Run On    R2    show running-config interface ${NAC_LOOPBACK}
    Should Contain    ${cfg}    description ${NAC_DESC}
    ...    R2 was not returned to the state the model declares
    Should Not Contain    ${cfg}    ${HAND_EDIT}
    Nac Plan Should Be Clean

Destroy Removes Everything The Model Created
    Nac Destroy
    FOR    ${r}    IN    @{ROUTERS}
        ${lo}=    Run On    ${r}    show running-config interface ${NAC_LOOPBACK}
        Should Not Contain    ${lo}    ${NAC_DESC}
        ...    ${r} still carries the Network as Code loopback after destroy
        ${acl}=    Run On    ${r}    show running-config | include ip access-list standard ${NAC_ACL}
        Should Not Contain    ${acl}    ${NAC_ACL}
        ...    ${r} still carries the Network as Code access list after destroy
    END
    ${count}=    Nac State Resource Count
    Should Be Equal As Integers    ${count}    0
    ...    the module still holds ${count} resources in state after destroy

The Two Approaches Do Not Contend For The Same Objects
    [Documentation]    Both suites push a loopback and a standard access list to
    ...                the same three routers. If they ever named the same
    ...                object, each would revert the other and the symptom would
    ...                be an intermittent failure in whichever ran second.
    ${model}=    Read Nac Model
    FOR    ${d}    IN    @{model}[iosxe][devices]
        Should Be Equal As Integers    ${d}[configuration][interfaces][loopbacks][0][id]    98
        ...    the Network as Code model no longer owns Loopback98; check it has
        ...    not moved onto Loopback99, which the RESTCONF suite manages
        Should Be Equal    ${d}[configuration][access_lists][standard][0][name]    ${NAC_ACL}
    END
