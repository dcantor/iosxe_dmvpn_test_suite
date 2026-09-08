*** Settings ***
Documentation     Destructive tests: things breaking, and what survives.
...
...               The rest of the suite breaks things gently -- a cleared cache, a
...               blocked protocol, a mismatched key. These take the fabric apart
...               while traffic is running and assert what is still standing
...               afterwards, which is where a design's real shape shows.
...
...               Every test here restores what it broke, in a teardown that runs
...               whether the test passed or failed, and the suite teardown repeats
...               the restoration unconditionally. A destructive test that fails to
...               clean up does not fail alone -- it fails every suite that runs
...               after it, for reasons that look nothing like the cause.
Resource          ../resources/c8000v.resource
Library           String
Library           Collections
# the MTU blackhole test drives a Linux host, so the host sessions are
# opened here too rather than discovered missing mid-suite
Suite Setup       Run Keywords    Open All Routers    AND    Open All Hosts
Suite Teardown    Run Keywords    Restore Everything    AND    Close All Connections

*** Variables ***
${SPOKE_ACL}       BLOCK-SPOKE
${R2_LAN_IF}       GigabitEthernet3
${SHORT_HOLDTIME}  60
${OVERSIZE}        1472
${OFF_KEY}         WrongKey
${OFF_TUNNEL_KEY}  999

*** Test Cases ***
A Shortcut Outlives The Hub, But Its Routing Does Not
    [Documentation]    The claim worth testing rather than assuming. A spoke-to-
    ...                spoke tunnel is genuinely direct: the NHRP mapping and the
    ...                IPsec session are between the spokes and the hub is not on
    ...                the path. So the hub going away should not break it.
    ...
    ...                Except that it does, one layer up. Both spokes learn each
    ...                other's prefixes from BGP, and both peer only with the hub.
    ...                Lose the hub and BFD tears those sessions down in about two
    ...                seconds, the prefixes withdraw, and there is no route to put
    ...                on the tunnel -- which is still sitting there, perfectly
    ...                healthy, carrying nothing.
    ...
    ...                So this asserts both halves: the tunnel address still
    ...                answers, and the loopback behind it does not. The data plane
    ...                is hub-independent here; the control plane is not.
    [Teardown]    Restore Hub Tunnel
    Establish Shortcut
    Configure On    R1    interface ${DMVPN_TUNNEL}    shutdown
    Wait Until Keyword Succeeds    12x    5s    Route Should Be Gone    R2    ${R3_BGP_PREFIX}

    ${nhrp}=    Run On    R2    show ip nhrp ${R3_DMVPN_IP}
    Should Contain    ${nhrp}    ${R3_WAN_IP}
    ...    the direct NHRP mapping did not survive the hub, so the tunnel was never direct
    ${sess}=    Run On    R2    show crypto session brief
    Should Contain    ${sess}    ${R3_WAN_IP}
    ...    the spoke-to-spoke IPsec session did not survive the hub

    ${direct}=    Run On    R2    ping ${R3_DMVPN_IP} source ${DMVPN_TUNNEL} repeat 5
    Should Contain    ${direct}    Success rate is 100 percent
    ...    the direct tunnel stopped carrying traffic when the hub went away
    ${routed}=    Run On    R2    ping ${R3_BGP_PREFIX} source Loopback1 repeat 5
    Should Contain    ${routed}    Success rate is 0 percent
    ...    the spoke still routes to the far loopback with the hub down, so the
    ...    control plane is not as hub-dependent as this test assumes

The Fabric Comes Back When The Hub Does
    [Documentation]    Recovery without operator action beyond restoring the hub:
    ...                registration, BGP and the shortcut all return on their own.
    Wait Until Keyword Succeeds    24x    5s    Hub Should Hold Both Registrations
    Wait Until Keyword Succeeds    24x    5s    Route Should Exist    R2    ${R3_BGP_PREFIX}
    Establish Shortcut
    ${trace}=    Run On    R2    traceroute ${R3_BGP_PREFIX} source Loopback1 probe 1 timeout 1 numeric
    Should Contain    ${trace}    ${R3_DMVPN_IP}
    Should Not Contain    ${trace}    ${R1_DMVPN_IP}
    ...    the shortcut did not re-form after the hub returned

Blocking The Spokes At The Underlay Falls Back Through The Hub
    [Documentation]    The realistic partial failure: two sites that can both reach
    ...                the hub but not each other, which is what happens whenever a
    ...                firewall between branches permits the head end and nothing
    ...                else. Resolution cannot complete, so no shortcut forms -- and
    ...                connectivity must survive anyway, through the hub.
    ...
    ...                The suite's other fallback test only clears the cache, which
    ...                is the easy version: nothing is stopping the shortcut from
    ...                forming a moment later. Here it genuinely cannot.
    [Teardown]    Remove Spoke Block
    Configure On    R2    ip access-list extended ${SPOKE_ACL}
    ...    deny ip host ${R2_WAN_IP} host ${R3_WAN_IP}
    ...    deny ip host ${R3_WAN_IP} host ${R2_WAN_IP}
    ...    permit ip any any
    Configure On    R2    interface GigabitEthernet2    ip access-group ${SPOKE_ACL} in
    Run On    R2    clear ip nhrp
    Sleep    12s    reason=let the spoke re-register with the hub before probing

    ${out}=    Run On    R2    ping ${R3_BGP_PREFIX} source Loopback1 repeat 10
    ${rate}=    Get Regexp Matches    ${out}    Success rate is (\\d+) percent    1
    Should Be True    ${rate}[0] > 0
    ...    spoke-to-spoke connectivity was lost entirely; the hub fallback did not work
    ${nhrp}=    Run On    R2    show ip nhrp ${R3_DMVPN_IP}
    Should Not Contain    ${nhrp}    ${R3_WAN_IP}
    ...    a direct mapping formed even though the underlay between spokes is blocked
    ${trace}=    Run On    R2    traceroute ${R3_BGP_PREFIX} source Loopback1 probe 1 timeout 1 numeric
    Should Contain    ${trace}    ${R1_DMVPN_IP}
    ...    traffic is not transiting the hub, so it is not using the fallback:\n${trace}

An NHRP Authentication Mismatch Is Refused
    [Documentation]    The authentication string must match across the cloud. A
    ...                spoke that gets it wrong is refused registration and simply
    ...                never appears at the hub.
    ...
    ...                Both caches have to be cleared to see it. The hub holds its
    ...                registration entry for the full holdtime, so clearing only
    ...                the spoke leaves the hub answering from a stale cache -- and
    ...                the test reads "still registered" and concludes, wrongly,
    ...                that the mismatch had no effect.
    [Teardown]    Restore Spoke Tunnel Settings
    Configure On    R3    interface ${DMVPN_TUNNEL}    ip nhrp authentication ${OFF_KEY}
    Clear Nhrp Everywhere
    Wait Until Keyword Succeeds    12x    5s    Hub Should Not Hold Registration For    R3

A Tunnel Key Mismatch Fails Silently Instead
    [Documentation]    The same outcome by a different route, and the reason both
    ...                are worth having. A wrong authentication string is a
    ...                refusal. A wrong tunnel key is not refused by anything --
    ...                the GRE headers simply do not match, the packets are
    ...                discarded, and the tunnel interface goes on reporting itself
    ...                up with nothing passing through it.
    [Teardown]    Restore Spoke Tunnel Settings
    Configure On    R3    interface ${DMVPN_TUNNEL}    tunnel key ${OFF_TUNNEL_KEY}
    Clear Nhrp Everywhere
    Wait Until Keyword Succeeds    12x    5s    Hub Should Not Hold Registration For    R3
    ${state}=    Run On    R3    show ip interface brief | include ${DMVPN_TUNNEL}
    Should Match Regexp    ${state}    up\\s+up
    ...    the interface reported itself down, which would make this failure the
    ...    visible kind rather than the silent one this test exists to record

Blocking The Too-Big Message Blackholes Large Traffic
    [Documentation]    The classic silent MTU failure. The router tells a host
    ...                "fragmentation needed, MTU 1472" and the host adapts. Take
    ...                that message away and nothing announces the fault: small
    ...                packets keep working, ping keeps working, and anything bulk
    ...                stalls with no diagnostic anywhere.
    ...
    ...                The message is suppressed with "no ip unreachables" on the
    ...                interface it would leave by -- R2's LAN side, facing the
    ...                host. An outbound ACL was the obvious first choice and it
    ...                does not work: an outbound ACL does not filter traffic the
    ...                router originates, and this message is originated by R2.
    ...                Applying it to Tunnel0 does nothing either, for the same
    ...                reason -- the constraint is on the tunnel, but the message
    ...                is emitted towards the host.
    ...
    ...                Packet loss on its own proves nothing here: the oversized
    ...                ping fails either way, because the host is forbidden to
    ...                fragment it. What changes is whether anything says why, so
    ...                the assertions are about the diagnostic and not the loss.
    ...
    ...                This is what makes the boundary the MTU suite measures
    ...                matter, and it is why that suite asserts the host learns the
    ...                path MTU rather than merely that big packets fail.
    [Setup]       Wait For Converged Fabric
    [Teardown]    Remove Pmtu Block
    Flush Host Route Cache    H2
    ${learned}=    Run On Host    H2    ping -c 2 -W 2 -M do -s ${OVERSIZE} ${H3_IP}
    Should Contain    ${learned}    mtu = ${TUNNEL_MTU}
    ...    the host did not learn the path MTU even before anything was blocked

    Configure On    R2    interface ${R2_LAN_IF}    no ip unreachables
    Flush Host Route Cache    H2

    ${blind}=    Run On Host    H2    ping -c 3 -W 2 -M do -s ${OVERSIZE} ${H3_IP}
    Should Contain    ${blind}    100% packet loss
    ...    large traffic got through even with the too-big message suppressed
    Should Not Contain    ${blind}    mtu = ${TUNNEL_MTU}
    ...    the host still learned the MTU, so the message was not actually suppressed
    Should Not Contain    ${blind}    Frag needed
    ...    the host was still told fragmentation was needed, so the failure is not
    ...    the silent kind this test exists to record
    ${small}=    Run On Host    H2    ping -c 2 -W 2 ${H3_IP}
    Should Contain    ${small}    , 0% packet loss
    ...    small packets failed too, so this is an outage rather than a blackhole

NHRP Mappings Are Soft State And Age Out
    [Documentation]    A shortcut is a cache entry, not configuration: it exists
    ...                because traffic justified it and it should disappear when
    ...                that stops being true. Proven with a shortened holdtime --
    ...                the configured 300s would add five minutes to every run for
    ...                a property that is no truer at 300 than at 60.
    ...
    ...                Expiry is not punctual. NHRP ages entries lazily, and a 60s
    ...                holdtime was measured clearing at about 170s, so the wait
    ...                here is generous rather than exact.
    [Setup]       Wait For Converged Fabric
    [Teardown]    Restore Holdtime
    Set Holdtime On Spokes    ${SHORT_HOLDTIME}
    Clear Nhrp Everywhere
    Sleep    15s    reason=let both spokes register again at the shorter holdtime
    Establish Shortcut
    Wait Until Keyword Succeeds    30x    10s    Direct Mapping Should Be Absent    R2    R3
    Establish Shortcut
    Direct Mapping Should Exist    R2    R3

*** Keywords ***
Establish Shortcut
    Run On    R2    ping ${R3_BGP_PREFIX} source Loopback1 repeat 10
    Wait Until Keyword Succeeds    12x    5s    Direct Mapping Should Exist    R2    R3

Direct Mapping Should Exist
    [Arguments]    ${alias}    ${peer}
    ${out}=    Run On    ${alias}    show ip nhrp ${${peer}_DMVPN_IP}
    Should Contain    ${out}    ${${peer}_WAN_IP}
    ...    ${alias} holds no direct mapping for ${peer}

Direct Mapping Should Be Absent
    [Arguments]    ${alias}    ${peer}
    ${out}=    Run On    ${alias}    show ip nhrp ${${peer}_DMVPN_IP}
    Should Not Contain    ${out}    ${${peer}_WAN_IP}
    ...    ${alias} still holds a direct mapping for ${peer}

Route Should Be Gone
    [Arguments]    ${alias}    ${prefix}
    ${out}=    Run On    ${alias}    show ip route ${prefix}
    Should Contain    ${out}    not in table
    ...    ${alias} still has a route to ${prefix}

Route Should Exist
    [Arguments]    ${alias}    ${prefix}
    ${out}=    Run On    ${alias}    show ip route ${prefix}
    Should Contain    ${out}    Known via
    ...    ${alias} has not relearned ${prefix}

Hub Should Hold Both Registrations
    ${out}=    Run On    R1    show dmvpn
    FOR    ${r}    IN    R2    R3
        Should Contain    ${out}    ${${r}_WAN_IP}    ${r} is not registered at the hub
    END

Hub Should Not Hold Registration For
    [Arguments]    ${peer}
    ${out}=    Run On    R1    show dmvpn | include 100.64.0
    Should Not Contain    ${out}    ${${peer}_WAN_IP}
    ...    the hub still holds a registration for ${peer}

Clear Nhrp Everywhere
    [Documentation]    Both sides, always. The hub's own entry outlives a spoke
    ...                side clear for the whole holdtime.
    FOR    ${r}    IN    @{ROUTERS}
        Run On    ${r}    clear ip nhrp
    END

Set Holdtime On Spokes
    [Arguments]    ${seconds}
    FOR    ${r}    IN    R2    R3
        Configure On    ${r}    interface ${DMVPN_TUNNEL}    ip nhrp holdtime ${seconds}
    END

Flush Host Route Cache
    [Arguments]    ${host}
    Run On Host    ${host}    sudo ip route flush cache

Wait For Converged Fabric
    [Documentation]    Restoration is not finished when the configuration is back.
    ...                It is finished when the fabric is carrying traffic again.
    ...
    ...                These come back at very different speeds. NHRP registration
    ...                returns within seconds of the tunnel recovering, but the BGP
    ...                session rides that tunnel and needs about a minute more. A
    ...                teardown that waits only for registration therefore reports
    ...                success while the routing table is still empty, and the next
    ...                test opens on a cloud that looks healthy and carries nothing
    ...                -- which fails somewhere far away from the cause.
    Wait Until Keyword Succeeds    24x    5s    Hub Should Hold Both Registrations
    Wait Until Keyword Succeeds    36x    5s    Route Should Exist    R2    ${R3_BGP_PREFIX}
    Wait Until Keyword Succeeds    36x    5s    Route Should Exist    R3    ${R2_BGP_PREFIX}
    Wait Until Keyword Succeeds    12x    5s    Spokes Should Reach Each Other

Spokes Should Reach Each Other
    ${out}=    Run On    R2    ping ${R3_BGP_PREFIX} source Loopback1 repeat 5
    Should Contain    ${out}    Success rate is 100 percent
    ...    the spokes cannot reach each other end to end, so the fabric is not converged

# ---- teardowns: each restores one thing, and Restore Everything repeats them
Restore Hub Tunnel
    Run Keyword And Ignore Error    Configure On    R1    interface ${DMVPN_TUNNEL}    no shutdown
    Run Keyword And Ignore Error    Wait For Converged Fabric

Remove Spoke Block
    Run Keyword And Ignore Error    Configure On    R2    interface GigabitEthernet2
    ...    no ip access-group ${SPOKE_ACL} in
    Run Keyword And Ignore Error    Configure On    R2    no ip access-list extended ${SPOKE_ACL}
    Run Keyword And Ignore Error    Run On    R2    clear ip nhrp
    Run Keyword And Ignore Error    Wait For Converged Fabric

Remove Pmtu Block
    Run Keyword And Ignore Error    Configure On    R2    interface ${R2_LAN_IF}
    ...    ip unreachables
    Run Keyword And Ignore Error    Flush Host Route Cache    H2

Restore Spoke Tunnel Settings
    Run Keyword And Ignore Error    Configure On    R3    interface ${DMVPN_TUNNEL}
    ...    tunnel key ${NHRP_NETWORK_ID}    ip nhrp authentication ${NHRP_AUTH}
    Run Keyword And Ignore Error    Clear Nhrp Everywhere
    Run Keyword And Ignore Error    Wait For Converged Fabric

Restore Holdtime
    Run Keyword And Ignore Error    Set Holdtime On Spokes    ${NHRP_HOLDTIME}
    Run Keyword And Ignore Error    Clear Nhrp Everywhere
    Run Keyword And Ignore Error    Wait For Converged Fabric

Restore Everything
    [Documentation]    Repeated unconditionally at suite level. Any of these may
    ...                already have run in a test teardown; running twice costs a
    ...                few seconds, and not running at all costs every suite that
    ...                follows.
    Run Keyword And Ignore Error    Restore Hub Tunnel
    Run Keyword And Ignore Error    Remove Spoke Block
    Run Keyword And Ignore Error    Remove Pmtu Block
    Run Keyword And Ignore Error    Restore Spoke Tunnel Settings
    Run Keyword And Ignore Error    Restore Holdtime
    Run Keyword And Ignore Error    Wait For Converged Fabric
