*** Settings ***
Documentation     DMVPN Phase 3: one multipoint tunnel, NHRP, and dynamic
...               spoke-to-spoke paths.
...
...               The static VTI lab this mirrors built a tunnel per spoke with a
...               configured destination at each end. Here there is one mGRE
...               interface per router and no destination anywhere: NHRP supplies
...               it. A spoke registers its NBMA address with the hub, and a spoke
...               that wants another spoke asks for its address rather than being
...               told in advance.
...
...               The tests that matter are the ones about the shortcut. A hub-
...               and-spoke overlay that never forms a direct path is a working
...               VPN but it is not DMVPN, and every configuration assertion here
...               would pass just as well against one. So the suite clears the
...               NHRP cache, proves the direct path is absent, sends traffic, and
...               then requires it to exist and to be used.
Resource          ../resources/c8000v.resource
Library           String
Library           Collections
Suite Setup       Open All Routers
Suite Teardown    Run Keywords    Restore Nhrp    AND    Close All Connections

*** Variables ***
&{DMVPN_IP}       R1=${R1_DMVPN_IP}    R2=${R2_DMVPN_IP}    R3=${R3_DMVPN_IP}
&{WAN_IP}         R1=${R1_WAN_IP}      R2=${R2_WAN_IP}      R3=${R3_WAN_IP}
&{BGP_PREFIX}     R1=${R1_BGP_PREFIX}  R2=${R2_BGP_PREFIX}  R3=${R3_BGP_PREFIX}
${SETTLE}         10s

*** Test Cases ***
Every Router Runs One Multipoint Tunnel With No Destination
    [Documentation]    The structural difference from a static VTI. A configured
    ...                destination would make this point-to-point again and there
    ...                would be nothing for NHRP to resolve.
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config interface ${DMVPN_TUNNEL}
        Should Contain    ${cfg}    tunnel mode gre multipoint
        ...    ${r}'s tunnel is not multipoint
        Should Not Contain    ${cfg}    tunnel destination
        ...    ${r} has a configured tunnel destination, which defeats NHRP
        Should Contain    ${cfg}    tunnel source GigabitEthernet2
        Should Contain    ${cfg}    ip address ${DMVPN_IP}[${r}]
    END
    ${count}=    Run On    R1    show ip interface brief | count Tunnel
    Should Contain    ${count}    Number of lines which match regexp = 1
    ...    the hub has more than one tunnel interface, which is the VTI shape

The Tunnel Is Protected By IPsec On Every Router
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config interface ${DMVPN_TUNNEL}
        Should Contain    ${cfg}    tunnel protection ipsec profile
    END

NHRP Shares A Network ID And Authentication Everywhere
    [Documentation]    Both must match across the cloud; a mismatch in either
    ...                leaves registrations silently unanswered.
    FOR    ${r}    IN    @{ROUTERS}
        ${cfg}=    Run On    ${r}    show running-config interface ${DMVPN_TUNNEL}
        Should Contain    ${cfg}    ip nhrp network-id ${NHRP_NETWORK_ID}
        Should Contain    ${cfg}    ip nhrp authentication ${NHRP_AUTH}
    END

The Hub Is The Next Hop Server And The Spokes Point At It
    FOR    ${r}    IN    R2    R3
        ${cfg}=    Run On    ${r}    show running-config interface ${DMVPN_TUNNEL}
        Should Contain    ${cfg}    ip nhrp nhs ${R1_DMVPN_IP} nbma ${R1_WAN_IP}
        ...    ${r} does not name the hub as its next hop server
    END
    ${hub}=    Run On    R1    show running-config interface ${DMVPN_TUNNEL}
    Should Not Contain    ${hub}    ip nhrp nhs
    ...    the hub points at a next hop server, so it is behaving as a spoke
    # "ip nhrp map multicast dynamic" is accepted by this release but never
    # rendered in the running configuration, so its presence is asserted through
    # what it does -- the hub holding registrations it was never configured
    # with -- rather than through text that will not be there.
    Hub Should Have Both Spokes Registered

This Is Phase 3, Not Phase 1 Or 2
    [Documentation]    Redirect on the hub and shortcut on the spokes are what
    ...                make the overlay reorganise itself. Without them the tests
    ...                below about direct paths cannot pass, and the design is a
    ...                different one.
    ${hub}=    Run On    R1    show running-config interface ${DMVPN_TUNNEL}
    Should Contain    ${hub}    ip nhrp redirect    the hub sends no NHRP redirects
    # "ip nhrp shortcut" is likewise accepted but not rendered, so the spoke half
    # of Phase 3 is asserted by the shortcut tests below rather than by grepping
    # for a line this release does not print.
    FOR    ${r}    IN    R2    R3
        ${cfg}=    Run On    ${r}    show running-config interface ${DMVPN_TUNNEL}
        Should Contain    ${cfg}    ip nhrp nhs
        ...    ${r} has no next hop server, so it cannot be a Phase 3 spoke
    END

Both Spokes Register With The Hub
    [Documentation]    Registration is dynamic: the hub is configured with no
    ...                spoke addresses at all and learns them as they arrive.
    Wait Until Keyword Succeeds    12x    5s    Hub Should Have Both Spokes Registered

The Hub Maps Each Spoke's Tunnel Address To Its NBMA Address
    ${cache}=    Run On    R1    show ip nhrp
    FOR    ${r}    IN    R2    R3
        Should Match Regexp    ${cache}    (?s)${DMVPN_IP}[${r}]/32.*?${WAN_IP}[${r}]
        ...    the hub has no NBMA mapping for ${r}
    END
    Should Contain    ${cache}    registered

Every DMVPN Peering Is Encrypted
    [Documentation]    One IPsec profile protects the multipoint tunnel, so each
    ...                peering formed over it -- including ones the configuration
    ...                never named -- is protected by construction.
    FOR    ${r}    IN    R2    R3
        ${sess}=    Run On    ${r}    show crypto session brief
        Should Contain    ${sess}    ${R1_WAN_IP}
        ...    ${r} has no IPsec session with the hub
        # matched on the session row, not the whole output: the legend at the top
        # spells out "D - Down" and a substring check finds it every time
        Should Match Regexp    ${sess}    ${R1_WAN_IP}\\s+Tu0\\s+.*UA
        ...    ${r}'s session with the hub is not up and active
    END

A Spoke Learns The Far Spoke As The BGP Next Hop
    [Documentation]    The routing half of Phase 3, and the reason
    ...                "next-hop-unchanged" is configured on the hub. If the hub
    ...                rewrote the next hop to itself, every spoke-to-spoke prefix
    ...                would resolve to the hub, NHRP would never be asked to find
    ...                the far spoke, and no shortcut could form.
    ${out}=    Run On    R2    show bgp ipv4 unicast ${BGP_PREFIX}[R3]
    Should Contain    ${out}    ${R3_DMVPN_IP}
    ...    R2 does not see R3's tunnel address as the next hop for R3's prefix
    ${out}=    Run On    R3    show bgp ipv4 unicast ${BGP_PREFIX}[R2]
    Should Contain    ${out}    ${R2_DMVPN_IP}
    ...    R3 does not see R2's tunnel address as the next hop for R2's prefix

Spoke To Spoke Traffic Works Before Any Shortcut Exists
    [Documentation]    The fallback path. With the NHRP cache cleared there is no
    ...                direct entry, so the first packets go through the hub --
    ...                which is what makes the shortcut an optimisation rather
    ...                than a prerequisite for connectivity.
    Clear Spoke Shortcuts
    Direct Entry Should Be Absent    R2    R3
    ${out}=    Run On    R2    ping ${BGP_PREFIX}[R3] source Loopback1 repeat 30
    Should Contain    ${out}    Success rate is
    ${loss}=    Get Regexp Matches    ${out}    Success rate is (\\d+) percent    1
    Should Be True    ${loss}[0] > 0
    ...    no spoke-to-spoke traffic got through at all, via the hub or otherwise

A Shortcut Forms On Demand
    [Documentation]    The defining behaviour. Cleared first so the entry cannot
    ...                be left over from an earlier test: it has to be created by
    ...                this traffic, here.
    Clear Spoke Shortcuts
    Direct Entry Should Be Absent    R2    R3
    Run On    R2    ping ${BGP_PREFIX}[R3] source Loopback1 repeat 20
    Wait Until Keyword Succeeds    12x    5s    Direct Entry Should Exist    R2    R3
    Wait Until Keyword Succeeds    12x    5s    Direct Entry Should Exist    R3    R2

Traffic Then Leaves The Hub Out Of The Path
    [Documentation]    The point of the shortcut, and the strongest statement this
    ...                suite makes: with the direct path installed, a trace from
    ...                one spoke to the other reaches it in a single hop instead
    ...                of transiting the hub.
    Wait Until Keyword Succeeds    12x    5s    Direct Entry Should Exist    R2    R3
    ${trace}=    Run On    R2    traceroute ${BGP_PREFIX}[R3] source Loopback1 probe 1 timeout 1 numeric
    Should Contain    ${trace}    ${R3_DMVPN_IP}
    Should Not Contain    ${trace}    ${R1_DMVPN_IP}
    ...    the trace still passes through the hub, so no shortcut is in use:\n${trace}
    ${hops}=    Get Regexp Matches    ${trace}    (?m)^\\s+(\\d+) \\d+\\.\\d+\\.\\d+\\.\\d+    1
    Should Be Equal As Integers    ${hops}[-1]    1
    ...    the far spoke is ${hops}[-1] hops away, expected 1

The Shortcut Gets Its Own IPsec Session
    [Documentation]    A direct path between two routers that were never
    ...                configured with each other's addresses, protected all the
    ...                same, because the profile is bound to the tunnel rather
    ...                than to a peer.
    Wait Until Keyword Succeeds    12x    5s    Direct Entry Should Exist    R2    R3
    ${sess}=    Run On    R2    show crypto session brief
    Should Contain    ${sess}    ${R3_WAN_IP}
    ...    R2 has no IPsec session with R3's NBMA address:\n${sess}
    ${count}=    Get Regexp Matches    ${sess}    (?m)^\\d+\\.\\d+\\.\\d+\\.\\d+\\s+Tu0    0
    Length Should Be    ${count}    2
    ...    R2 holds ${count} tunnel sessions, expected one to the hub and one to R3

*** Keywords ***
Hub Should Have Both Spokes Registered
    ${out}=    Run On    R1    show dmvpn
    FOR    ${r}    IN    R2    R3
        Should Match Regexp    ${out}    ${WAN_IP}[${r}]\\s+${DMVPN_IP}[${r}]\\s+UP
        ...    ${r} is not registered and up at the hub
    END
    ${dynamic}=    Get Regexp Matches    ${out}    (?m)UP\\s+\\S+\\s+D
    Length Should Be    ${dynamic}    2
    ...    the hub does not show two dynamically registered peers

Direct Entry Should Exist
    [Arguments]    ${alias}    ${peer}
    ${out}=    Run On    ${alias}    show ip nhrp ${DMVPN_IP}[${peer}]
    Should Contain    ${out}    ${WAN_IP}[${peer}]
    ...    ${alias} has no NHRP entry mapping ${peer} to its NBMA address

Direct Entry Should Be Absent
    [Arguments]    ${alias}    ${peer}
    ${out}=    Run On    ${alias}    show ip nhrp ${DMVPN_IP}[${peer}]
    Should Not Contain    ${out}    ${WAN_IP}[${peer}]
    ...    ${alias} still holds a direct entry for ${peer}, so nothing was cleared

Clear Spoke Shortcuts
    [Documentation]    Drops learned entries on both spokes. The statically
    ...                configured next-hop-server mapping is not affected, so the
    ...                spokes stay registered with the hub.
    FOR    ${r}    IN    R2    R3
        Run On    ${r}    clear ip nhrp
    END
    Sleep    ${SETTLE}    reason=let the spokes re-register before anything is asserted

Restore Nhrp
    Run Keyword And Ignore Error    Clear Spoke Shortcuts
    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    12x    5s
    ...    Hub Should Have Both Spokes Registered
