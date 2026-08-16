"""
RMOG 2026 Live Auction Tracker  —  Alex M (Burrito Engineer)
Streamlit app.  Run with:  streamlit run auction_tracker.py

Superflex keeper league. Budget $305, 0 keepers signed.
Columns:
  draft   = 2025 auction price
  keep    = 1-yr sign cost (drafted + $15; $15 if dropped -> $0 basis)
  val     = estimated 2026 auction value (superflex, our scoring)
  surplus = val - keep  (positive = a keeper bargain; the +$15 tax makes
            almost everything negative)
"""

import streamlit as st
import pandas as pd

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
BUDGET = 305
MAX_QB_ACTIVE = 3          # rulebook: max 3 QB on active roster
TOTAL_SLOTS = 15           # 1QB 2RB 2WR 1TE 1SF 2FLEX 1DEF + 5 bench
STARTER_NEED = {"QB": 2, "RB": 2, "WR": 3, "TE": 1, "DEF": 1}  # incl. superflex

POS_COLORS = {"QB": "#c2410c", "RB": "#15803d", "WR": "#1d4ed8",
              "TE": "#7c3aed", "DEF": "#57534e"}

# (name, pos, draft, dropped(0/1), keep1yr, value, surplus, last_team)
PLAYERS = [
    ("Ja'Marr Chase", 'WR', 61, 0, 76, 62, -14, "Marcedes Lewis's Fan Club"),
    ('Justin Jefferson', 'WR', 59, 0, 74, 60, -14, "Falco's Sentinels"),
    ('Saquon Barkley', 'RB', 53, 0, 68, 58, -10, 'RB U'),
    ('Jahmyr Gibbs', 'RB', 45, 0, 60, 55, -5, "Curt's Amazing Team"),
    ('Patrick Mahomes', 'QB', 42, 0, 57, 52, -5, 'PilloPantz Troll'),
    ('Joe Burrow', 'QB', 48, 0, 63, 50, -13, "Curt's Amazing Team"),
    ('Ashton Jeanty', 'RB', 36, 0, 51, 46, -5, 'They Hit the Second Bower'),
    ('Jaxon Smith-Njigba', 'WR', 23, 0, 38, 44, 6, 'Busch Boys'),
    ("De'Von Achane", 'RB', 27, 0, 42, 44, 2, 'Nacua Matata'),
    ('Josh Jacobs', 'RB', 44, 0, 59, 42, -17, 'RB U'),
    ('Jonathan Taylor', 'RB', 30, 0, 45, 40, -5, 'Busch Boys'),
    ('Derrick Henry', 'RB', 41, 0, 56, 38, -18, 'RB U'),
    ('Drake London', 'WR', 27, 0, 42, 38, -4, 'RB U'),
    ('Christian McCaffrey', 'RB', 33, 0, 48, 34, -14, 'RB U'),
    ('Tee Higgins', 'WR', 34, 0, 49, 34, -15, "Marcedes Lewis's Fan Club"),
    ('Emeka Egbuka', 'WR', 18, 0, 33, 32, -1, 'Burrito Engineer'),
    ('Marvin Harrison Jr.', 'WR', 24, 0, 39, 30, -9, 'RB U'),
    ('TreVeyon Henderson', 'RB', 20, 0, 35, 30, -5, 'Busch Boys'),
    ('James Cook III', 'RB', 21, 0, 36, 30, -6, "Curt's Amazing Team"),
    ('Justin Herbert', 'QB', 19, 0, 34, 30, -4, "Falco's Sentinels"),
    ('Omarion Hampton', 'RB', 26, 0, 41, 30, -11, "Falco's Sentinels"),
    ('A.J. Brown', 'WR', 24, 0, 39, 30, -9, "Marcedes Lewis's Fan Club"),
    ('Dak Prescott', 'QB', 25, 0, 40, 30, -10, 'Nacua Matata'),
    ('Garrett Wilson', 'WR', 15, 0, 30, 30, 0, 'Nacua Matata'),
    ('Tetairoa McMillan', 'WR', 20, 0, 35, 30, -5, 'Burrito Engineer'),
    ('Rome Odunze', 'WR', 8, 0, 23, 28, 5, "Curt's Amazing Team"),
    ('Terry McLaurin', 'WR', 22, 0, 37, 24, -13, 'They Hit the Second Bower'),
    ('Jared Goff', 'QB', 15, 0, 30, 24, -6, 'PilloPantz Troll'),
    ('Kenneth Walker III', 'RB', 22, 0, 37, 24, -13, 'PilloPantz Troll'),
    ('Drake Maye', 'QB', 9, 0, 24, 22, -2, 'RB U'),
    ('Xavier Worthy', 'WR', 9, 0, 24, 22, -2, "Falco's Sentinels"),
    ('Cam Skattebo', 'RB', 1, 0, 16, 22, 6, "Falco's Sentinels"),
    ('David Montgomery', 'RB', 29, 0, 44, 22, -22, 'They Hit the Second Bower'),
    ('Zay Flowers', 'WR', 17, 0, 32, 22, -10, "Marcedes Lewis's Fan Club"),
    ('Quinshon Judkins', 'RB', 2, 0, 17, 22, 5, 'Nacua Matata'),
    ('Chuba Hubbard', 'RB', 19, 0, 34, 22, -12, 'Burrito Engineer'),
    ('Mike Evans', 'WR', 20, 0, 35, 20, -15, 'They Hit the Second Bower'),
    ('Trevor Lawrence', 'QB', 15, 1, 15, 20, 5, 'They Hit the Second Bower'),
    ('Tyreek Hill', 'WR', 20, 1, 15, 20, 5, 'Team Nifty Nick'),
    ('George Kittle', 'TE', 13, 0, 28, 18, -10, 'Busch Boys'),
    ('Caleb Williams', 'QB', 6, 0, 21, 18, -3, "Falco's Sentinels"),
    ('J.J. McCarthy', 'QB', 18, 0, 33, 18, -15, 'Burrito Engineer'),
    ('Alvin Kamara', 'RB', 16, 0, 31, 16, -15, "Curt's Amazing Team"),
    ('DK Metcalf', 'WR', 12, 0, 27, 16, -11, "Falco's Sentinels"),
    ('RJ Harvey', 'RB', 14, 1, 15, 16, 1, "Marcedes Lewis's Fan Club"),
    ('Sam LaPorta', 'TE', 10, 0, 25, 16, -9, 'Nacua Matata'),
    ('George Pickens', 'WR', 12, 0, 27, 16, -11, 'PilloPantz Troll'),
    ('Jameson Williams', 'WR', 9, 0, 24, 14, -10, "Falco's Sentinels"),
    ('DJ Moore', 'WR', 13, 0, 28, 14, -14, 'Team Nifty Nick'),
    ("D'Andre Swift", 'RB', 12, 0, 27, 13, -14, 'They Hit the Second Bower'),
    ('Jaylen Warren', 'RB', 11, 0, 26, 12, -14, "Curt's Amazing Team"),
    ('Davante Adams', 'WR', 10, 0, 25, 12, -13, "Curt's Amazing Team"),
    ('Ricky Pearsall', 'WR', 19, 1, 15, 12, -3, 'Team Nifty Nick'),
    ('Bryce Young', 'QB', 7, 1, 15, 12, -3, 'PilloPantz Troll'),
    ('Jordan Addison', 'WR', 8, 0, 23, 10, -13, "Curt's Amazing Team"),
    ('Jayden Reed', 'WR', 2, 0, 17, 10, -7, 'They Hit the Second Bower'),
    ('Jauan Jennings', 'WR', 10, 0, 25, 10, -15, 'Team Nifty Nick'),
    ('Jordan Mason', 'RB', 5, 0, 20, 10, -10, 'Team Nifty Nick'),
    ('Cam Ward', 'QB', 5, 0, 20, 10, -10, 'PilloPantz Troll'),
    ('T.J. Hockenson', 'TE', 6, 1, 15, 10, -5, 'Burrito Engineer'),
    ('Broncos', 'DEF', 9, 1, 15, 9, -6, 'Nacua Matata'),
    ('Travis Kelce', 'TE', 8, 0, 23, 8, -15, 'Busch Boys'),
    ('Matthew Stafford', 'QB', 3, 0, 18, 8, -10, "Curt's Amazing Team"),
    ('Khalil Shakir', 'WR', 7, 0, 22, 8, -14, "Curt's Amazing Team"),
    ('Chris Olave', 'WR', 5, 0, 20, 8, -12, "Falco's Sentinels"),
    ('Aaron Jones Sr.', 'RB', 8, 0, 23, 8, -15, "Marcedes Lewis's Fan Club"),
    ('Jerry Jeudy', 'WR', 3, 0, 18, 8, -10, 'Team Nifty Nick'),
    ('Tyler Warren', 'TE', 6, 0, 21, 8, -13, 'PilloPantz Troll'),
    ('Josh Downs', 'WR', 6, 0, 21, 8, -13, 'PilloPantz Troll'),
    ('Zach Charbonnet', 'RB', 8, 0, 23, 8, -15, 'Burrito Engineer'),
    ('Trey Benson', 'RB', 1, 0, 16, 8, -8, 'Burrito Engineer'),
    ('Sam Darnold', 'QB', 1, 1, 15, 6, -9, 'RB U'),
    ('Chris Godwin Jr.', 'WR', 6, 0, 21, 6, -15, 'Busch Boys'),
    ('Tyrone Tracy Jr.', 'RB', 5, 0, 20, 6, -14, "Falco's Sentinels"),
    ('Travis Etienne Jr.', 'RB', 6, 0, 21, 6, -15, 'They Hit the Second Bower'),
    ('Mark Andrews', 'TE', 5, 1, 15, 6, -9, 'Team Nifty Nick'),
    ('Michael Pittman Jr.', 'WR', 3, 0, 18, 6, -12, 'PilloPantz Troll'),
    ('David Njoku', 'TE', 3, 1, 15, 6, -9, 'Burrito Engineer'),
    ('Brandon Aiyuk', 'WR', 1, 0, 16, 6, -10, 'Burrito Engineer'),
    ('Steelers', 'DEF', 5, 1, 15, 5, -10, "Marcedes Lewis's Fan Club"),
    ('Travis Hunter', 'WR', 5, 1, 15, 5, -10, 'Nacua Matata'),
    ('Darnell Mooney', 'WR', 4, 1, 15, 4, -11, 'RB U'),
    ('Joe Mixon', 'RB', 4, 0, 19, 4, -15, 'Busch Boys'),
    ('Dallas Goedert', 'TE', 2, 1, 15, 4, -11, "Marcedes Lewis's Fan Club"),
    ('Javonte Williams', 'RB', 3, 0, 18, 3, -15, 'Busch Boys'),
    ('Jakobi Meyers', 'WR', 3, 0, 18, 3, -15, 'Busch Boys'),
    ('J.K. Dobbins', 'RB', 3, 0, 18, 3, -15, "Curt's Amazing Team"),
    ('Stefon Diggs', 'WR', 3, 1, 15, 3, -12, 'Nacua Matata'),
    ('Eagles', 'DEF', 3, 1, 15, 3, -12, 'Burrito Engineer'),
    ('Oronde Gadsden', 'TE', 0, 0, 15, 1, -14, 'RB U'),
    ('Bhayshul Tuten', 'RB', 1, 0, 16, 1, -15, 'RB U'),
    ('Browns', 'DEF', 0, 1, 15, 1, -14, 'RB U'),
    ('Shedeur Sanders', 'QB', 0, 0, 15, 1, -14, 'RB U'),
    ('Kareem Hunt', 'RB', 0, 1, 15, 1, -14, 'RB U'),
    ('Aaron Rodgers', 'QB', 0, 0, 15, 1, -14, 'Busch Boys'),
    ("Wan'Dale Robinson", 'WR', 0, 0, 15, 1, -14, 'Busch Boys'),
    ('Rams', 'DEF', 0, 1, 15, 1, -14, 'Busch Boys'),
    ('Jake Ferguson', 'TE', 0, 0, 15, 1, -14, 'Busch Boys'),
    ('Devin Singletary', 'RB', 0, 1, 15, 1, -14, 'Busch Boys'),
    ('Deebo Samuel Sr.', 'WR', 0, 0, 15, 1, -14, "Curt's Amazing Team"),
    ('Harold Fannin Jr.', 'TE', 0, 0, 15, 1, -14, "Curt's Amazing Team"),
    ('Texans', 'DEF', 1, 1, 15, 1, -14, "Curt's Amazing Team"),
    ('Kyle Pitts Sr.', 'TE', 0, 0, 15, 1, -14, "Curt's Amazing Team"),
    ('Vikings', 'DEF', 1, 0, 16, 1, -15, "Falco's Sentinels"),
    ('Chris Rodriguez Jr.', 'RB', 0, 0, 15, 1, -14, "Falco's Sentinels"),
    ('Alec Pierce', 'WR', 0, 1, 15, 1, -14, "Falco's Sentinels"),
    ('Luther Burden III', 'WR', 0, 0, 15, 1, -14, "Falco's Sentinels"),
    ('Jaxson Dart', 'QB', 0, 0, 15, 1, -14, 'They Hit the Second Bower'),
    ('Dalton Schultz', 'TE', 1, 1, 15, 1, -14, 'They Hit the Second Bower'),
    ('Bills', 'DEF', 1, 1, 15, 1, -14, 'They Hit the Second Bower'),
    ('Quentin Johnston', 'WR', 0, 1, 15, 1, -14, 'They Hit the Second Bower'),
    ('Rhamondre Stevenson', 'RB', 1, 0, 16, 1, -15, 'They Hit the Second Bower'),
    ('Rico Dowdle', 'RB', 0, 0, 15, 1, -14, "Marcedes Lewis's Fan Club"),
    ('Theo Johnson', 'TE', 0, 1, 15, 1, -14, "Marcedes Lewis's Fan Club"),
    ('Sean Tucker', 'RB', 0, 0, 15, 1, -14, "Marcedes Lewis's Fan Club"),
    ('Tyler Shough', 'QB', 0, 1, 15, 1, -14, "Marcedes Lewis's Fan Club"),
    ('Hunter Henry', 'TE', 0, 1, 15, 1, -14, 'Nacua Matata'),
    ('Michael Wilson', 'WR', 0, 0, 15, 1, -14, 'Nacua Matata'),
    ('Brenton Strange', 'TE', 0, 1, 15, 1, -14, 'Nacua Matata'),
    ('Colby Parkinson', 'TE', 0, 0, 15, 1, -14, 'Nacua Matata'),
    ('Blake Corum', 'RB', 0, 1, 15, 1, -14, 'Nacua Matata'),
    ('Michael Carter', 'WR', 0, 1, 15, 1, -14, 'Nacua Matata'),
    ('Parker Washington', 'WR', 0, 1, 15, 1, -14, 'Nacua Matata'),
    ('Woody Marks', 'RB', 0, 0, 15, 1, -14, 'Team Nifty Nick'),
    ('Kenny Gainwell', 'RB', 0, 1, 15, 1, -14, 'Team Nifty Nick'),
    ('Chargers', 'DEF', 0, 1, 15, 1, -14, 'Team Nifty Nick'),
    ('Darren Waller', 'TE', 0, 0, 15, 1, -14, 'Team Nifty Nick'),
    ('Troy Franklin', 'WR', 0, 1, 15, 1, -14, 'Team Nifty Nick'),
    ('Tyler Allgeier', 'RB', 1, 1, 15, 1, -14, 'Team Nifty Nick'),
    ('Daniel Jones', 'QB', 0, 1, 15, 1, -14, 'Team Nifty Nick'),
    ('Devin Neal', 'RB', 0, 0, 15, 1, -14, 'Team Nifty Nick'),
    ('Juwan Johnson', 'TE', 0, 1, 15, 1, -14, 'PilloPantz Troll'),
    ('Seahawks', 'DEF', 0, 1, 15, 1, -14, 'PilloPantz Troll'),
    ('Christian Watson', 'WR', 0, 0, 15, 1, -14, 'PilloPantz Troll'),
    ('Rashid Shaheed', 'WR', 1, 0, 16, 1, -15, 'PilloPantz Troll'),
    ('Chimere Dike', 'WR', 0, 1, 15, 1, -14, 'PilloPantz Troll'),
    ('Jacoby Brissett', 'QB', 0, 0, 15, 1, -14, 'Burrito Engineer'),
    ('Romeo Doubs', 'WR', 0, 0, 15, 1, -14, 'Burrito Engineer'),
    ('Kyle Monangai', 'RB', 0, 1, 15, 1, -14, 'Burrito Engineer'),
    ('Keenan Allen', 'WR', 0, 0, 15, 1, -14, 'Burrito Engineer'),
    ('Jayden Higgins', 'WR', 1, 0, 16, 1, -15, 'Burrito Engineer'),
    ('Tyrod Taylor', 'QB', 0, 1, 15, 1, -14, 'Burrito Engineer'),
    ('Luke Musgrave', 'TE', 0, 0, 15, 1, -14, 'Burrito Engineer'),]

COLS = ["name", "pos", "draft", "dropped", "keep", "val", "surplus", "team"]
POOL_DF = pd.DataFrame(PLAYERS, columns=COLS)
POOL_DF["dropped"] = POOL_DF["dropped"].astype(bool)

# ----------------------------------------------------------------------------
# STATE
# ----------------------------------------------------------------------------
st.set_page_config(page_title="RMOG 2026 Auction Tracker", layout="wide")

def init():
    if "taken" not in st.session_state:
        st.session_state.taken = {}      # name -> "mine" or "gone"
    if "mine" not in st.session_state:
        st.session_state.mine = []       # list of dict(name, pos, price)
    if "gone" not in st.session_state:
        st.session_state.gone = []       # list of dict(name, pos, price)
    if "trades" not in st.session_state:
        st.session_state.trades = []     # list of dict(desc, dollars)

init()

def spent_auction():
    return sum(m["price"] for m in st.session_state.mine)

def trade_net():
    return sum(t["dollars"] for t in st.session_state.trades)

def remaining():
    return BUDGET - spent_auction() - trade_net()

def slots_left():
    return max(0, TOTAL_SLOTS - len(st.session_state.mine))

def max_bid_now():
    sl = slots_left()
    r = remaining()
    return r - (sl - 1) if sl > 0 else r

def my_pos_counts():
    c = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "DEF": 0}
    for m in st.session_state.mine:
        c[m["pos"]] += 1
    return c

def buy_mine(name, pos, price):
    st.session_state.taken[name] = "mine"
    st.session_state.mine.append({"name": name, "pos": pos, "price": int(price)})

def mark_gone(name, pos, price):
    st.session_state.taken[name] = "gone"
    st.session_state.gone.append({"name": name, "pos": pos, "price": int(price)})

def undo_mine(idx):
    item = st.session_state.mine.pop(idx)
    st.session_state.taken.pop(item["name"], None)

def undo_gone(idx):
    item = st.session_state.gone.pop(idx)
    st.session_state.taken.pop(item["name"], None)

# ----------------------------------------------------------------------------
# HEADER + MONEY DASHBOARD
# ----------------------------------------------------------------------------
st.title("RMOG 2026 — Live Auction Tracker")
st.caption("Burrito Engineer (Alex M) · superflex keeper · $305 · 0 keepers signed "
           "· **keep** = drafted+$15 · **surplus** = value − keep")

rem = remaining()
sl = slots_left()
mb = max_bid_now()
per_slot = (rem / sl) if sl > 0 else 0
pos_counts = my_pos_counts()
qb_cap_hit = pos_counts["QB"] >= MAX_QB_ACTIVE

c1, c2, c3, c4 = st.columns(4)
c1.metric("Remaining", f"${rem}",
          delta=f"of ${BUDGET}", delta_color="off")
c2.metric("Max bid now", f"${max(0, mb)}",
          delta="keeps $1 / open slot", delta_color="off")
c3.metric("Avg $ / slot left", f"${per_slot:.1f}",
          delta=f"{sl} of {TOTAL_SLOTS} open", delta_color="off")
c4.metric("Roster" + (" · QB CAP!" if qb_cap_hit else ""),
          f"{len(st.session_state.mine)}/{TOTAL_SLOTS}",
          delta=f"QB{pos_counts['QB']} RB{pos_counts['RB']} WR{pos_counts['WR']} "
                f"TE{pos_counts['TE']} DEF{pos_counts['DEF']}",
          delta_color="off")

if rem < 0 or mb < 0:
    st.error("You're over budget — undo a purchase or lower a bid.")
if qb_cap_hit:
    st.warning(f"QB cap reached ({MAX_QB_ACTIVE} max on active roster).")

# positional needs line
need_bits = []
for p, need in STARTER_NEED.items():
    have = pos_counts[p]
    icon = "✅" if have >= need else "⬜"
    need_bits.append(f"{icon} {p} {have}/{need}")
st.markdown("**Starters:** " + "  ·  ".join(need_bits))
st.markdown("💡 **Keeper bargains** (only players whose value beats the +$15 tax): "
            "Jaxon Smith-Njigba, Cam Skattebo, Rome Odunze, Quinshon Judkins")

st.divider()
left, right = st.columns([1.6, 1])

# ----------------------------------------------------------------------------
# LEFT: AVAILABLE POOL
# ----------------------------------------------------------------------------
with left:
    st.subheader("Available players")

    f1, f2, f3 = st.columns([2, 1.4, 1])
    search = f1.text_input("Search", "", placeholder="Player name…",
                           label_visibility="collapsed")
    pos_filter = f2.selectbox("Position", ["ALL", "QB", "RB", "WR", "TE", "DEF"],
                              label_visibility="collapsed")
    bargains_only = f3.toggle("Bargains only")

    taken_names = set(st.session_state.taken.keys())
    df = POOL_DF[~POOL_DF["name"].isin(taken_names)].copy()
    if pos_filter != "ALL":
        df = df[df["pos"] == pos_filter]
    if bargains_only:
        df = df[df["surplus"] > 0]
    if search.strip():
        df = df[df["name"].str.contains(search.strip(), case=False, regex=False)]
    df = df.sort_values("val", ascending=False).reset_index(drop=True)

    st.caption(f"{len(df)} players · draft = 2025 price · keep = drafted+$15 · "
               f"val = 2026 est · surplus = val − keep")

    # header row
    h = st.columns([0.5, 3, 0.8, 0.8, 0.8, 0.9, 1.1, 1.6])
    for col, txt in zip(h, ["Pos", "Player", "Drft", "Keep", "Val", "Surp", "Bid $", ""]):
        col.markdown(f"<span style='font-size:11px;color:#a8a29e;font-weight:700'>{txt}</span>",
                     unsafe_allow_html=True)

    # scrollable-ish: show top N to keep the page snappy
    MAX_SHOW = 60
    shown = df.head(MAX_SHOW)
    for _, r in shown.iterrows():
        name = r["name"]
        color = POS_COLORS.get(r["pos"], "#78716c")
        cols = st.columns([0.5, 3, 0.8, 0.8, 0.8, 0.9, 1.1, 1.6])
        cols[0].markdown(
            f"<span style='background:{color};color:#fff;font-size:10px;"
            f"font-weight:800;border-radius:4px;padding:2px 5px'>{r['pos']}</span>",
            unsafe_allow_html=True)
        badge = (f" <span style='background:#dcfce7;color:#15803d;font-size:9px;"
                 f"font-weight:800;border-radius:3px;padding:1px 4px'>KEEP+{r['surplus']}</span>"
                 if r["surplus"] > 0 else "")
        subtitle = f"{r['team']}" + (" · was dropped" if r["dropped"] else "")
        cols[1].markdown(
            f"<b>{name}</b>{badge}<br>"
            f"<span style='font-size:10px;color:#a8a29e'>{subtitle}</span>",
            unsafe_allow_html=True)
        cols[2].markdown(f"<span style='color:#a8a29e'>{r['draft'] or '–'}</span>",
                         unsafe_allow_html=True)
        cols[3].markdown(f"<span style='color:#78716c'>{r['keep']}</span>",
                         unsafe_allow_html=True)
        cols[4].markdown(f"<b style='color:{color}'>{r['val']}</b>",
                         unsafe_allow_html=True)
        surp_color = "#15803d" if r["surplus"] > 0 else "#cbcbcb"
        surp_txt = f"+{r['surplus']}" if r["surplus"] > 0 else str(r["surplus"])
        cols[5].markdown(f"<b style='color:{surp_color}'>{surp_txt}</b>",
                         unsafe_allow_html=True)
        bid = cols[6].number_input("bid", min_value=0, value=int(r["val"]),
                                   key=f"bid_{name}", label_visibility="collapsed")
        bcol1, bcol2 = cols[7].columns(2)
        if bcol1.button("Mine", key=f"mine_{name}", use_container_width=True):
            buy_mine(name, r["pos"], bid)
            st.rerun()
        if bcol2.button("Gone", key=f"gone_{name}", use_container_width=True):
            mark_gone(name, r["pos"], bid)
            st.rerun()

    if len(df) > MAX_SHOW:
        st.caption(f"Showing top {MAX_SHOW} by value. Use search or a position "
                   f"filter to narrow to the rest ({len(df) - MAX_SHOW} more).")

# ----------------------------------------------------------------------------
# RIGHT: MY ROSTER · TRADES · OFF THE BOARD
# ----------------------------------------------------------------------------
with right:
    # --- My roster ---
    st.subheader(f"My roster · ${spent_auction()} on players")
    if not st.session_state.mine:
        st.caption("Set a bid, hit “Mine”. The bid box defaults to my value estimate.")
    for i, m in enumerate(st.session_state.mine):
        color = POS_COLORS.get(m["pos"], "#78716c")
        val = int(POOL_DF.loc[POOL_DF["name"] == m["name"], "val"].iloc[0]) \
            if (POOL_DF["name"] == m["name"]).any() else m["price"]
        over = f" <span style='color:#dc2626;font-size:11px'>(+{m['price']-val} over val)</span>" \
            if m["price"] > val else ""
        rc = st.columns([4, 1])
        rc[0].markdown(
            f"<b style='color:{color}'>{m['pos']}</b> {m['name']} — "
            f"<b>${m['price']}</b>{over}", unsafe_allow_html=True)
        if rc[1].button("undo", key=f"un_mine_{i}"):
            undo_mine(i)
            st.rerun()

    st.divider()

    # --- Pre-draft trades ---
    tn = trade_net()
    tn_label = f"−${tn} to budget" if tn > 0 else f"+${-tn} to budget"
    st.subheader("Pre-draft trades")
    st.caption(f"Net effect: {tn_label}  ·  auction $ sent (+) lowers budget, "
               f"received (−) raises it. Signing a traded player? Log his keeper "
               f"cost (drafted+$15) as a separate entry.")
    tc = st.columns([3, 1, 1])
    tdesc = tc[0].text_input("desc", "", placeholder="Got Skattebo, sent Benson",
                             key="tdesc", label_visibility="collapsed")
    tamt = tc[1].number_input("amt", value=0, step=1, key="tamt",
                              label_visibility="collapsed")
    if tc[2].button("Log", use_container_width=True):
        if tdesc.strip():
            st.session_state.trades.append({"desc": tdesc.strip(), "dollars": int(tamt)})
            st.rerun()
    for i, t in enumerate(st.session_state.trades):
        amt_txt = f"−${t['dollars']}" if t["dollars"] > 0 else f"+${-t['dollars']}"
        amt_color = "#dc2626" if t["dollars"] > 0 else "#15803d"
        rc = st.columns([4, 1])
        rc[0].markdown(f"{t['desc']} — <b style='color:{amt_color}'>{amt_txt}</b>",
                       unsafe_allow_html=True)
        if rc[1].button("×", key=f"un_tr_{i}"):
            st.session_state.trades.pop(i)
            st.rerun()

    st.divider()

    # --- Off the board ---
    st.subheader(f"Off the board · {len(st.session_state.gone)}")
    if not st.session_state.gone:
        st.caption("Log rivals’ buys to watch their budgets drain.")
    for i, g in enumerate(st.session_state.gone):
        color = POS_COLORS.get(g["pos"], "#78716c")
        rc = st.columns([4, 1])
        rc[0].markdown(
            f"<span style='color:#78716c'><b style='color:{color}'>{g['pos']}</b> "
            f"{g['name']} — ${g['price']}</span>", unsafe_allow_html=True)
        if rc[1].button("undo", key=f"un_gone_{i}"):
            undo_gone(i)
            st.rerun()

# ----------------------------------------------------------------------------
# SIDEBAR: reset
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Draft controls")
    st.write(f"Budget: **${BUDGET}**")
    st.write(f"Players bought: **{len(st.session_state.mine)}**")
    st.write(f"Off board: **{len(st.session_state.gone)}**")
    st.write(f"Trades logged: **{len(st.session_state.trades)}**")
    st.divider()
    if st.button("↺ Reset everything", type="secondary"):
        for k in ("taken", "mine", "gone", "trades"):
            st.session_state.pop(k, None)
        st.rerun()
    st.caption("State lives in this browser session. A reset or full page reload "
               "clears the draft.")
