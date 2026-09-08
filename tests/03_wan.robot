*** Settings ***
Documentation     The shared WAN underlay that DMVPN is built on.
...
...               This is where the mirrored lab departs from the one it copies.
...               The static VTI lab gave each spoke a private /30 to the hub and
...               asserted the spokes had *no* path to each other -- correct
...               there, and fatal here. A spoke can only build a direct tunnel to
...               another spoke if it can reach that spoke's NBMA address, so the
...               test below is the exact inverse of its counterpart.
...
...               The segment carries the underlay and nothing else: no site
...               prefixes, no routing protocol, no reachability to anything
...               behind a router. Everything of substance rides the tunnel.
Resource          ../resources/c8000v.resource
Library           String
Suite Setup       Open All Routers
Suite Teardown    Close All Connections

*** Variables ***
&{WAN_IP}         R1=${R1_WAN_IP}    R2=${R2_WAN_IP}    R3=${R3_WAN_IP}
&{LAN_NET}        R1=${R1_LAN_NET}   R2=${R2_LAN_NET}   R3=${R3_LAN_NET}

*** Test Cases ***
Every Router Is On The Shared WAN Segment
    FOR    ${r}    IN    @{ROUTERS}
        ${out}=    Run On    ${r}    show ip interface brief | include GigabitEthernet2
        Should Match Regexp    ${out}    GigabitEthernet2\\s+${WAN_IP}[${r}]\\s+YES\\s+\\S+\\s+up\\s+up
        ...    ${r}'s WAN interface is not up with the expected address
    END

Every Router Can Reach Every Other Router On It
    [Documentation]    Including spoke to spoke, which is the precondition for a
    ...                direct tunnel and the property the VTI lab deliberately did
    ...                not have. Tested at the underlay, before any tunnel exists.
    FOR    ${from}    IN    @{ROUTERS}
        FOR    ${to}    IN    @{ROUTERS}
            Continue For Loop If    '${from}' == '${to}'
            Ping Should Fully Succeed    ${from}    ${WAN_IP}[${to}]    repeat 5
        END
    END

The Spokes Reach Each Other Directly, Not Through The Hub
    [Documentation]    One hop at the underlay. If this became two the spokes
    ...                would still have connectivity, and DMVPN would still form
    ...                tunnels -- but every "direct" spoke-to-spoke path would
    ...                quietly be transiting the hub anyway.
    ${trace}=    Run On    R2    traceroute ${R3_WAN_IP} probe 1 timeout 1 numeric
    Should Contain    ${trace}    ${R3_WAN_IP}
    Should Not Contain    ${trace}    ${R1_WAN_IP}
    ...    the spokes reach each other via the hub at the underlay:\n${trace}

Each Router Learns The Others On The Segment
    [Documentation]    A shared segment, so every router should have resolved
    ...                every other -- unlike a point-to-point link with exactly
    ...                one neighbour.
    FOR    ${r}    IN    @{ROUTERS}
        ${arp}=    Run On    ${r}    show ip arp GigabitEthernet2
        FOR    ${peer}    IN    @{ROUTERS}
            Continue For Loop If    '${peer}' == '${r}'
            Should Contain    ${arp}    ${WAN_IP}[${peer}]
            ...    ${r} has not resolved ${peer} on the WAN segment
        END
    END

The Underlay Carries No Site Prefixes
    [Documentation]    The WAN is a transport, not a routing domain. A site
    ...                prefix appearing here would mean traffic could reach a LAN
    ...                without ever entering the tunnel -- unencrypted, and
    ...                invisible to every test that watches the overlay.
    FOR    ${r}    IN    @{ROUTERS}
        ${out}=    Run On    ${r}    show ip route | include GigabitEthernet2
        FOR    ${peer}    IN    @{ROUTERS}
            Should Not Contain    ${out}    ${LAN_NET}[${peer}]
            ...    ${peer}'s LAN is routed out the WAN interface on ${r}, which
            ...    would put site traffic on the underlay instead of the tunnel
        END
        Should Contain    ${out}    ${WAN_NET}
        ...    ${r} does not route the WAN segment out its WAN interface at all
    END

No Routing Protocol Runs On The WAN Segment
    [Documentation]    BGP peers over the tunnel, so the underlay should carry no
    ...                adjacency at all. One here would be a second, unprotected
    ...                path for the control plane.
    FOR    ${r}    IN    @{ROUTERS}
        ${out}=    Run On    ${r}    show bgp ipv4 unicast summary | begin Neighbor
        Should Not Contain    ${out}    ${WAN_NET.rsplit('.', 2)[0]}.
        ...    ${r} has a BGP neighbour on the WAN underlay rather than the tunnel
    END
