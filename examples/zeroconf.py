from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import stubborn_sets
from helpers import display_graph

# %%
server = MDP(
    [
        (
            "tau",
            ("s0", "x<=0"),
            ({("ip:=1", "s1"): 0.5, ("ip:=2", "s1"): 0.5}),
        ),
        (
            "send_used",
            ("s1", "x=20 & ip=2 & probes<4"),
            ("probes:=probes+1, x:=0", "s1"),
        ),
        (
            "send_fresh",
            ("s1", "x=20 & ip=1 & probes<4"),
            ("probes:=probes+1, x:=0", "s1"),
        ),
        ("tau", ("s1", "x=20 & probes=4"), ("x:=0", "s2")),
        ("recv", ("s1", "x<=20"), ("x:=0, ip:=0, probes:=0", "s0")),
        ("tau", ("s1", "x<20"), ("x:=x+1", "s1")),
        ("tau", ("s2", "x<20"), ("x:=x+1", "s2")),
    ],
    name="server",
)

print(server)


# %%
client = MDP(
    [
        ("send_fresh", ("e0", "y<5"), ("y:=y+1", "e0")),
        ("send_used", "e0", {("y:=0", "e0"): 0.1, ("y:=0", "e1"): 0.9}),
        (
            "tau",
            ("e1", "y<=5 & y>=1"),
            {("y:=0", "e0"): 0.1, ("y:=0", "e2"): 0.9},
        ),
        ("recv", ("e2", "y<=5 & y>=1"), ("y:=0", "e0")),
    ],
    name="client",
)

print(client)


# %%
display_graph(server, client, file_path="out/graphs/zeroconf_modules.gv")

# %%
system = MDP(server, client)

print(system)

# %%
display_graph(
    system, file_path="out/graphs/zeroconf_system.gv", set_method=stubborn_sets
)
