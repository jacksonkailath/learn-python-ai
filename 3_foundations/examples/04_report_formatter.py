"""Generate a weekly team summary report."""
import datetime


def make_report(team, week, done, open_tasks, blockers):
    """Return the formatted weekly report as one string."""
    w = 44
    total = done + open_tasks
    pct = done / total * 100 #12/(4+12) * 100 = 75.0
    title = f"{team} — Week {week}" #Data Platform — Week 27
    out = []
    #[1,23,31,"haha",55,69] ordered , 
    # 0  1  2  3      4  5
    out.append("=" * w)
    #["========..."]
    out.append(title.center(w))
    #["========...","   Data Platform — Week 27   "]
    out.append("=" * w)
    out.append(f"Generated on: {datetime.date.today():%Y-%m-%d}")
    #["========...","   Data Platform — Week 27   ","========..."]
    out.append(f"Tasks completed:  {done}")
    #["========...","   Data Platform — Week 27   ","========...","Tasks completed:  12"]
    out.append(f"Tasks still open: {open_tasks}")
    out.append(f"Completion rate:  {pct:.1f}%")
    out.append(f"Blockers:         {blockers}")
    out.append("~" * w)
    out.append(f"Report generated for {team} — share in the Monday stand-up channel.")
    out.append("=" * w)
    #["========...","   Data Platform — Week 27   ","========...","Tasks completed:  12",.....]
    return "\n".join(out)
#str.join("\n",out)


if __name__ == "__main__":
    report = make_report("Data Platform", 27, 12, 4, "None reported")
    print(report)
    #print("string1 \n string2")
