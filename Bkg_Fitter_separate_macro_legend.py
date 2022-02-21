#! /usr/bin/env python

###
### Macro used for fitting the background and saving the fits as a rooWorkspace for use by combine.
###

import ROOT
from ROOT import gStyle, gROOT, RooFit, RooAbsData, RooAbsReal, RooDataHist, RooArgList
from ROOT import TLatex, TCanvas, TLine, TFile, RooBinning, TLegend

from array import array

gStyle.SetOptStat(0)

gROOT.SetBatch(True)

def extract_workspace(input_file, workspace_name, model_name, variable_name, signal=False, data_name="data_obs", data_inside=True):
    root_file = TFile.Open(input_file)
    workspace = root_file.Get(workspace_name)
    if signal:
        data_obs = workspace.var(model_name+"_norm").getValV() # abuse of variable name
    else:
        if data_inside:
            data_obs = workspace.data(data_name)
            data_obs.SetName("data_obs")
        else:
            data_obs = None
    pdf = workspace.pdf(model_name)
    variable = workspace.var(variable_name)
    if not "Dijet" in variable.GetTitle():
        variable.SetTitle("Dijet Mass (GeV)")
    return data_obs, pdf, variable

def setTopPad(TopPad, r=4, small_gap=False):
    TopPad.SetPad("TopPad", "", 0., 1./r, 1.0, 1.0, 0, -1, 0)
    #TopPad.SetTopMargin(0.24/r)
    TopPad.SetTopMargin(0.28/r)
    if small_gap:
        TopPad.SetBottomMargin(2*0.01/r)
    else:
        TopPad.SetBottomMargin(2*0.04/r)
    TopPad.SetRightMargin(0.05)
    TopPad.SetLeftMargin(0.11)
    TopPad.SetTicks(1, 1)

def setBotPad(BotPad, r=4, small_gap=False):
    BotPad.SetPad("BotPad", "", 0., 0., 1.0, 1./r, 0, -1, 0)
    if small_gap:
        BotPad.SetTopMargin(0.1*r/100.)
    else:
        BotPad.SetTopMargin(0.5*r/100.)
    BotPad.SetBottomMargin(r/10.)
    BotPad.SetRightMargin(0.05)
    BotPad.SetLeftMargin(0.11)
    BotPad.SetTicks(1, 1)

def setPadStyle(h):
    h.GetXaxis().SetTitleSize(0)
    h.GetYaxis().SetTitleSize(0)
    h.GetXaxis().SetLabelSize(0)
    h.GetYaxis().SetLabelSize(0)

def setBotStyle(h, r=4, fixRange=True):
    h.GetXaxis().SetLabelSize(h.GetXaxis().GetLabelSize()*(r-1));
    h.GetXaxis().SetLabelOffset(h.GetXaxis().GetLabelOffset()*(r-1));
    h.GetXaxis().SetTitleSize(h.GetXaxis().GetTitleSize()*(r-1));
    h.GetYaxis().SetLabelSize(h.GetYaxis().GetLabelSize()*(r-1));
    h.GetYaxis().SetNdivisions(505);
    h.GetYaxis().SetTitleSize(h.GetYaxis().GetTitleSize()*(r-1));
    h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()/(r-1));
    if fixRange:
        h.GetYaxis().SetRangeUser(0., 2.)
        for i in range(1, h.GetNbinsX()+1):
            if h.GetBinContent(i)<1.e-6:
                h.SetBinContent(i, -1.e-6)

def drawCMS():
    latex_CMS = TLatex()
    latex_CMS.SetNDC()
    latex_CMS.SetTextSize(0.4)
    latex_CMS.SetTextColor(1)
    latex_CMS.SetTextFont(42)
    latex_CMS.SetTextAlign(12)
    latex_CMS.SetTextFont(62)
    latex_CMS.DrawLatex(0.115, 0.43, "CMS")

    text_lumi = "138 fb^{-1} (13 TeV)"
    latex_lumi = TLatex()
    latex_lumi.SetNDC()
    latex_lumi.SetTextAlign(32)
    latex_lumi.SetTextFont(42) #52
    latex_lumi.SetTextSize(0.15)
    latex_lumi.DrawLatex(0.90, 0.90, text_lumi)


def drawRegion_grid_plots(channel, year, lumi):
    text_year = str(year)
    latex_year = TLatex()
    latex_year.SetNDC()
    latex_year.SetTextAlign(12)
    latex_year.SetTextFont(42) #52
    latex_year.SetTextSize(0.07)
    latex_year.DrawLatex(0.16, 0.86, text_year)

    if isinstance(lumi, str):
        text_lumi = "%s fb^{-1}" % (lumi)
    else:
        if float(lumi)>1000000:
            text_lumi = "%.0f fb^{-1}" % (float(lumi)/1000.)
        else:
            text_lumi = "%.1f fb^{-1}" % (float(lumi)/1000.)
    latex_lumi = TLatex()
    latex_lumi.SetNDC()
    latex_lumi.SetTextAlign(32)
    latex_lumi.SetTextFont(42) #52
    latex_lumi.SetTextSize(0.07)
    latex_lumi.DrawLatex(0.88, 0.86, text_lumi)
    
def draw_legend_pad(X_mass, setData, plot_binning, output_file):
 
    c = TCanvas("c", "c", 3000, 300)
 
    frame = X_mass.frame()
    setPadStyle(frame)

    setData.plotOn(frame, RooFit.Binning(plot_binning), RooFit.Invisible())

    fit_color = 2
    fit_name = "Fit"
    setData.Clone("Fit").plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
        RooFit.LineColor(fit_color), RooFit.DrawOption("L"), RooFit.Name(fit_name))

    signal_color_bstar_2000 = 616
    signal_name_bstar_2000 = "b* Signal m2000"
    signal_color_Zprime_2000 = 433
    signal_name_Zprime_2000 = "Z' Signal m2000"
    signal_color_bstar_4000 = 617
    signal_name_bstar_4000 = "b* Signal m4000"
    signal_color_Zprime_4000 = 434
    signal_name_Zprime_4000 = "Z' Signal m4000"
    signal_color_bstar_6000 = 618
    signal_name_bstar_6000 = "b* Signal m6000"
    signal_color_Zprime_6000 = 435
    signal_name_Zprime_6000 = "Z' Signal m6000"

    setData.Clone("Zprime_2000").plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
        RooFit.LineColor(signal_color_Zprime_2000), RooFit.DrawOption("L"), RooFit.Name(signal_name_Zprime_2000))
    setData.Clone("Zprime_4000").plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
        RooFit.LineColor(signal_color_Zprime_4000), RooFit.DrawOption("L"), RooFit.Name(signal_name_Zprime_4000))
    setData.Clone("Zprime_6000").plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
        RooFit.LineColor(signal_color_Zprime_6000), RooFit.DrawOption("L"), RooFit.Name(signal_name_Zprime_6000))

    setData.Clone("bstar_2000").plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
        RooFit.LineColor(signal_color_bstar_2000), RooFit.DrawOption("L"), RooFit.Name(signal_name_bstar_2000))
    setData.Clone("bstar_4000").plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
        RooFit.LineColor(signal_color_bstar_4000), RooFit.DrawOption("L"), RooFit.Name(signal_name_bstar_4000))
    setData.Clone("bstar_6000").plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
        RooFit.LineColor(signal_color_bstar_6000), RooFit.DrawOption("L"), RooFit.Name(signal_name_bstar_6000))

    frame.GetYaxis().SetTitle("")
    frame.GetYaxis().SetLabelSize(0.)
    frame.GetXaxis().SetTickLength(0)
    frame.GetYaxis().SetTickLength(0)
    frame.GetYaxis().SetRangeUser(10000,10001)
    frame.Draw()
    frame.SetTitle("")

    c.SetTopMargin(0.2)    
    #drawRegion(category, True, large=True)
    drawCMS()

    leg1 = TLegend(0.47, 0.1, 0.62, 0.78)
    leg1.SetBorderSize(0)
    leg1.SetFillStyle(0) #1001
    leg1.SetFillColor(0)

    # ridiculous workaround to retain control over marker in legend
    fake_hist = ROOT.TH1D("fake_hist", "fake_hist", 10, 0, 1) 
    fake_hist.SetMarkerStyle(8)
    fake_hist.SetMarkerColor(1)
    fake_hist.SetLineColor(1)
    fake_hist.Draw("SAME, E1")

    leg1.AddEntry(fake_hist.GetName(), "Data", "PEL")
    leg1.AddEntry(fit_name, fit_name, "L")#.SetTextColor(629)
    leg1.SetY1(0.78-leg1.GetNRows()*0.22)
    leg1.Draw()

    leg2 = TLegend(0.58, 0.1, 0.73, 0.78)
    leg2.SetBorderSize(0)
    leg2.SetFillStyle(0) #1001
    leg2.SetFillColor(0)
    leg2.AddEntry("Z' Signal m2000", "Z', m=2000 GeV", "L")
    leg2.AddEntry("Z' Signal m4000", "Z', m=4000 GeV", "L")
    leg2.AddEntry("Z' Signal m6000", "Z', m=6000 GeV", "L")
    leg2.SetY1(0.78-leg2.GetNRows()*0.22)
    leg2.Draw()

    leg3 = TLegend(0.74, 0.1, 0.89, 0.78)
    leg3.SetBorderSize(0)
    leg3.SetFillStyle(0) #1001
    leg3.SetFillColor(0)
    leg3.AddEntry("b* Signal m2000", "b*, m=2000 GeV", "L")
    leg3.AddEntry("b* Signal m4000", "b*, m=4000 GeV", "L")
    leg3.AddEntry("b* Signal m6000", "b*, m=6000 GeV", "L")
    leg3.SetY1(0.78-leg3.GetNRows()*0.22)
    leg3.Draw()

    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextFont(42)

    text = TLatex()
    text.SetTextColor(1)
    text.SetTextFont(42)
    text.SetTextAlign(12)
    text.SetTextSize(0.15)
    text.DrawLatexNDC(0.27, 0.42, "#splitline{Wide PF-jets}{#splitline{m_{jj} > 1.53 TeV, |#Delta#eta| < 1.1}{|#eta| < 2.5, p_{T} > 30 GeV}}")
    text.Draw("SAME")

    c.SaveAs(output_file)

X_MIN = 1530
X_MAX = 7800 #8200

dijet_bins = [1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176, 197, 220, 244, 270, 296, 325, 354, 386, 419, 453, 489, 526, 565, 606, 649, 693, 740, 788, 838, 890, 944, 1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060, 7320, 7589, 7866, 8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430, 10798, 11179, 11571, 11977, 12395, 12827, 13272, 13732, 14000]

bins = [x for x in dijet_bins if x>=X_MIN and x<=X_MAX]
X_min = min(bins)
X_max = max(bins)
abins = array( 'd', bins )
plot_binning = RooBinning(len(abins)-1, abins)

some_dummy_input = "workspace/medium/data_2016_bb.root"
some_dummy_workspace = "Zprime_2016"
some_dummy_model = "Bkg_2016_bb"
some_dummy_variable = "jj_mass_widejet"
some_dummy_data_name = "data_obs"
output_file = "bstar_bkg_plots/legend_pad.pdf"

setData, modelBkg, X_mass = extract_workspace(some_dummy_input, some_dummy_workspace, some_dummy_model,
    some_dummy_variable, data_name=some_dummy_data_name, data_inside=True)


draw_legend_pad(X_mass, setData, plot_binning, output_file)


