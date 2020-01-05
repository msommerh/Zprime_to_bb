
import ROOT

m = [1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000]
y = [3.3625061681471835, 2.800330141951287, 3.403344657005455, 4.193426487852318, 4.475824613919622, 5.076983197789659, 5.149745038893322, 6.048451689701748, 4.975928645894235, 4.962159148253382, 6.5941932264790175, 11.197700484957945]

gy = ROOT.TGraph()
fy = ROOT.TF1("func","pol3", 0, 10000)

n=0
for i,mp in enumerate(m):
    gy.SetPoint(n, mp, y[i])
    n+=1


gy.Fit(fy, "Q0", "SAME")

print fy.GetFormula().Print()
print 'p0:',fy.GetFormula().GetParameter('p0')
print 'p1:',fy.GetFormula().GetParameter('p1')
print 'p2:',fy.GetFormula().GetParameter('p2')
print 'p3:',fy.GetFormula().GetParameter('p3')

gy.SetMarkerStyle(20)
gy.Draw()
fy.Draw("SAME")
