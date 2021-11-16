#! /usr/bin/env python

###
### Macro for creating the exclusion limits plots from a file of values.
###

import json
from array import array
from ROOT import gROOT, gStyle
from ROOT import TGraph, TGraphErrors, TGraphAsymmErrors
from ROOT import TCanvas
from ROOT import TLegend, TLatex, TText, TColor

#from utils import *

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-i", "--input", action="store", type="string", dest="input", default="example_limits.json")
parser.add_option("-o", "--output", action="store", type="string", dest="output", default="limit_plot.pdf")
(options, args) = parser.parse_args()
 
gStyle.SetOptStat(0)

gROOT.SetBatch(True)

with open(options.input) as json_file:
    INPUT = json.load(json_file)

def drawCMS(lumi, text, onTop=False, year='', suppressCMS=False, suppress_year=False):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(33)
    if (type(lumi) is float or type(lumi) is int):
        if float(lumi) > 0:
            latex.DrawLatex(0.95, 0.99, "%.0f fb^{-1}  (13 TeV)" % (float(lumi)/1000.))
        if year!='':
            if year=="run2": year="RunII"
            latex.DrawLatex(0.24, 0.99, year)
        elif float(lumi) > 0:
            if lumi==35920.:
                year = '2016'
            elif lumi==41530.:
                year = '2017'
            elif lumi==59740.:
                year = '2018'
            elif lumi==137190.:
                year = 'RunII'
            if not suppress_year:
                latex.DrawLatex(0.24, 0.99, year)
        else:
            latex.DrawLatex(0.9, 0.99, "(13 TeV)")
    elif type(lumi) is str: latex.DrawLatex(0.95, 0.985, "%s  (13 TeV)" % lumi)
    if not onTop: latex.SetTextAlign(11)
    latex.SetTextFont(62)
    latex.SetTextSize(0.05 if len(text)>0 else 0.06)
    if not suppressCMS:
        if not onTop: latex.DrawLatex(0.15, 0.88 if len(text)>0 else 0.85, "CMS")
        else: latex.DrawLatex(0.24, 0.9925, "CMS")
    latex.SetTextSize(0.04)
    latex.SetTextFont(52)
    if not onTop: latex.DrawLatex(0.15, 0.84, text)
    else: latex.DrawLatex(0.45, 0.98, text)


def draw():

    Obs0s = TGraph()
    Exp0s = TGraph()
    Exp1s = TGraphAsymmErrors()
    Exp2s = TGraphAsymmErrors()
    Theory = {}

    mass = list(INPUT["observed_values"].keys())
    mass.sort()

    for i, m in enumerate(mass):
        n = Exp0s.GetN()
        Obs0s.SetPoint(n, float(m), INPUT["observed_values"][m])
        Exp0s.SetPoint(n, float(m), INPUT["expected_values"][m])
        Exp1s.SetPoint(n, float(m), INPUT["expected_values"][m])
        Exp1s.SetPointError(n, 0., 0., INPUT["expected_values"][m]-INPUT["expected_minus1sigma_values"][m], INPUT["expected_plus1sigma_values"][m]-INPUT["expected_values"][m])
        Exp2s.SetPoint(n, float(m), INPUT["expected_values"][m])
        Exp2s.SetPointError(n, 0., 0., INPUT["expected_values"][m]-INPUT["expected_minus2sigma_values"][m], INPUT["expected_plus2sigma_values"][m]-INPUT["expected_values"][m])

    for t in INPUT["theory_order"]:
        Theory[t] = TGraphAsymmErrors()
        for m in sorted(INPUT["theory_values"][t].keys()):
            n = Theory[t].GetN()
            Theory[t].SetPoint(n, float(m), INPUT["theory_values"][t][m])
            Theory[t].SetPointError(n, 0., 0., INPUT["theory_uncert_down"][t][m], INPUT["theory_uncert_up"][t][m])
            Theory[t].SetLineColor(INPUT["theory_line_color"][t])
            Theory[t].SetFillColor(INPUT["theory_fill_color"][t])
            Theory[t].SetFillStyle(INPUT["theory_fill_style"][t])
            Theory[t].SetLineWidth(2)

    Exp2s.SetLineWidth(2)
    Exp2s.SetLineStyle(1)
    Obs0s.SetLineWidth(3)
    Obs0s.SetMarkerStyle(8)
    Obs0s.SetMarkerSize(0.75)
    Obs0s.SetLineColor(1)
    Exp0s.SetLineStyle(2)
    Exp0s.SetLineWidth(3)
    Exp1s.SetFillColor(417) #kGreen+1
    Exp1s.SetLineColor(417) #kGreen+1
    Exp2s.SetFillColor(800) #kOrange
    Exp2s.SetLineColor(800) #kOrange
    Exp2s.GetXaxis().SetTitle(INPUT["particle_label"]+" mass (GeV)")
    Exp2s.GetXaxis().SetTitleSize(Exp2s.GetXaxis().GetTitleSize()*1.25)
    Exp2s.GetXaxis().SetNoExponent(True)
    Exp2s.GetXaxis().SetMoreLogLabels(True)
    Exp2s.GetYaxis().SetTitle("#sigma("+INPUT["particle_label"]+") #bf{#it{#Beta}}("+INPUT["particle_label"]+" #rightarrow "+INPUT["decay_label"]+") #Alpha (fb)")
    Exp2s.GetYaxis().SetTitleOffset(1.5)
    Exp2s.GetYaxis().SetNoExponent(True)
    Exp2s.GetYaxis().SetMoreLogLabels()

    c1 = TCanvas("c1", "Exclusion Limits", 800, 600)
    c1.cd()
    c1.GetPad(0).SetTopMargin(0.06)
    c1.GetPad(0).SetRightMargin(0.05)
    c1.GetPad(0).SetLeftMargin(0.12)
    c1.GetPad(0).SetTicks(1, 1)
    c1.GetPad(0).SetLogy()
    Exp2s.Draw("A3")
    Exp1s.Draw("SAME, 3")
    for t in INPUT["theory_order"]:
        Theory[t].Draw("SAME, L3")
    Exp0s.Draw("SAME, L")
    Obs0s.Draw("SAME, PL")
    Exp2s.GetXaxis().SetTitleSize(0.050)
    Exp2s.GetYaxis().SetTitleSize(0.050)
    Exp2s.GetXaxis().SetLabelSize(0.045)
    Exp2s.GetYaxis().SetLabelSize(0.045)
    Exp2s.GetXaxis().SetTitleOffset(0.90)
    Exp2s.GetYaxis().SetTitleOffset(1.25)
    Exp2s.GetYaxis().SetMoreLogLabels(True)
    Exp2s.GetYaxis().SetNoExponent(True)
    Exp2s.GetYaxis().SetRangeUser(INPUT["Y_range"][0], INPUT["Y_range"][1])
    Exp2s.GetXaxis().SetRangeUser(INPUT["X_range"][0], INPUT["X_range"][1])
    drawCMS(137190., "", suppress_year=True) ##!!##

    # legend
    top = 0.9
    nitems = 4 + len(INPUT["theory_order"])

    leg = TLegend(0.53, top-nitems*0.3/5., 0.96, top)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetHeader("95% CL upper limits")
    leg.AddEntry(Obs0s, "Observed", "Pl")
    leg.AddEntry(Exp0s, "Expected", "l")
    leg.AddEntry(Exp1s, "#pm 1 std. deviation", "f")
    leg.AddEntry(Exp2s, "#pm 2 std. deviation", "f")
    for t in INPUT["theory_order"]:
        leg.AddEntry(Theory[t], INPUT["theory_label"][t], "fl")
    leg.Draw()
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextFont(42)

    leg2 = TLegend(0.12, 0.225-2*0.25/5., 0.65, 0.225)
    leg2.SetBorderSize(0)
    leg2.SetFillStyle(0) #1001
    leg2.SetFillColor(0)
    c1.GetPad(0).RedrawAxis()

    leg2.Draw()
    Obs0s.Draw("SAME, L")
    c1.GetPad(0).Update()
    c1.Print(options.output)

    
if __name__ == "__main__":
    draw()
