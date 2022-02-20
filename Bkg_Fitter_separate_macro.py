#! /usr/bin/env python

###
### Macro used for fitting the background and saving the fits as a rooWorkspace for use by combine.
###

import ROOT
from ROOT import gStyle, gROOT, RooFit, RooAbsData, RooAbsReal, RooDataHist, RooArgList
from ROOT import TLatex, TCanvas, TLine, TFile, RooBinning, TLegend

from array import array
import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-i", "--input", action="store", type="string", dest="input", default="example_workspace.root")
parser.add_option("-y", "--year", action="store", type="string", dest="year", default="2016")
parser.add_option("-p", "--parameters", action="store", type="string", dest="parameters", default="")
parser.add_option("-c", "--chi", action="store", type=float, dest="chi", default=0)
parser.add_option("-d", "--dof", action="store", type=int, dest="dof", default=0)
parser.add_option("-w", "--workspace_name", action="store", type="string", dest="workspace_name", default="Zprime_2018")
parser.add_option("-m", "--model_name", action="store", type="string", dest="model_name", default="Bkg_2018_bb")
parser.add_option("-v", "--variable_name", action="store", type="string", dest="variable_name", default="jj_mass_widejet")
parser.add_option("-n", "--data_name", action="store", type="string", dest="data_name", default="data_obs")
parser.add_option("-e", "--external_data_hist", action="store", type="string", dest="external_data_hist", default="")
parser.add_option("--category", action="store", type="string", dest="category", default="bb")
parser.add_option("-o", "--output", action="store", type="string", dest="output", default="bkg_plot.pdf")
parser.add_option("--signal_input", action="store", type="string", dest="signal_input", default="")
parser.add_option("--signal_workspace", action="store", type="string", dest="signal_workspace", default="Zprime_2018")
parser.add_option("--signal_norm_factor", action="store", type=float, dest="signal_norm_factor", default=1000.)
(options, args) = parser.parse_args()

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

def extract_signal_histogram(input_file, hist_name, variable):
    root_file = TFile.Open(input_file)
    hist = root_file.Get(hist_name)
    norm = hist.Integral()
    data_hist = RooDataHist(hist_name+"_datahist", hist_name+"_datahist", RooArgList(variable), hist)
    return norm, data_hist

def adjust_bstar_shape(roohist, m_range):
    points_to_remove = []
    for i in range(roohist.GetN()):
        roohist.SetPointEYlow(i, 0.)
        roohist.SetPointEYhigh(i, 0.)
        roohist.SetPointEXlow(i, 0.)
        roohist.SetPointEXhigh(i, 0.)
        if roohist.GetX()[i]<m_range[0] or roohist.GetX()[i]>m_range[1]:
            points_to_remove.append(i)
    for point in points_to_remove[::-1]: # remove backwards to preserve indexing
        roohist.RemovePoint(point)

def setTopPad(TopPad, r=4):
    TopPad.SetPad("TopPad", "", 0., 1./r, 1.0, 1.0, 0, -1, 0)
    #TopPad.SetTopMargin(0.24/r)
    TopPad.SetTopMargin(0.28/r)
    TopPad.SetBottomMargin(2*0.04/r)
    TopPad.SetRightMargin(0.05)
    TopPad.SetLeftMargin(0.11)
    TopPad.SetTicks(1, 1)

def setBotPad(BotPad, r=4):
    BotPad.SetPad("BotPad", "", 0., 0., 1.0, 1./r, 0, -1, 0)
    BotPad.SetTopMargin(0.5*r/100.)
    BotPad.SetBottomMargin(r/10.)
    BotPad.SetRightMargin(0.05)
    BotPad.SetLeftMargin(0.11)
    BotPad.SetTicks(1, 1)

def setPadStyle(h, r=1.2, isTop=False):
    h.GetXaxis().SetTitleSize(h.GetXaxis().GetTitleSize()*r*r)
    h.GetYaxis().SetTitleSize(h.GetYaxis().GetTitleSize()*r)
    h.GetXaxis().SetLabelSize(h.GetXaxis().GetLabelSize()*r)
    h.GetYaxis().SetLabelSize(h.GetYaxis().GetLabelSize()*r)
    if isTop: h.GetXaxis().SetLabelOffset(0.04)

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

def drawCMS(lumi, text, onTop=False, year='', suppressCMS=False, suppress_year=False, large=False):
    latex = TLatex()
    latex.SetNDC()
    if large:
        latex.SetTextSize(0.06)
        upper_margin = 0.98
    else:
        latex.SetTextSize(0.045)
        upper_margin = 0.99
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(33)
    if (type(lumi) is float or type(lumi) is int):
        if float(lumi) > 0:
            if float(lumi)>100000.:
                latex.DrawLatex(0.95, upper_margin+0.012, "%.0f fb^{-1}  (13 TeV)" % (float(lumi)/1000.))
            else:
                latex.DrawLatex(0.95, upper_margin+0.012, "%.1f fb^{-1}  (13 TeV)" % (float(lumi)/1000.))
        if year!='':
            if year=="run2": year="RunII"
            latex.DrawLatex(0.24, upper_margin, year)
        elif float(lumi) > 0:
            if lumi==35920. or lumi==36330.:
                year = '2016'
            elif lumi==41530.:
                year = '2017'
            elif lumi==59740.:
                year = '2018'
            elif lumi==137190. or lumi==137600.:
                year = 'RunII'
            if not suppress_year:
                latex.DrawLatex(0.24, upper_margin, year)
        else:
            latex.DrawLatex(0.9, upper_margin, "(13 TeV)")
    elif type(lumi) is str: latex.DrawLatex(0.95, 0.985, "%s  (13 TeV)" % lumi)
    if not onTop: latex.SetTextAlign(11)
    latex.SetTextFont(62)
    if large:
        latex.SetTextSize(0.07 if len(text)>0 else 0.08)
    else:
        latex.SetTextSize(0.05 if len(text)>0 else 0.06)
    if not suppressCMS:
        if not onTop:
            if large:
                latex.DrawLatex(0.15, 0.87 if len(text)>0 else 0.84, "CMS")
            else:
                latex.DrawLatex(0.15, 0.88 if len(text)>0 else 0.85, "CMS")
        else: latex.DrawLatex(0.24, 0.9925, "CMS")
    if large:
        latex.SetTextSize(0.05)
    else:
        latex.SetTextSize(0.04)
    latex.SetTextFont(52)
    if not onTop: latex.DrawLatex(0.15, 0.84, text)
    else: latex.DrawLatex(0.45, 0.98, text)

def getChannel(channel):
    text = ""
    if 'bg' in channel: text += "#geq 1 b tag"
    elif 'bb' in channel or '2b' in channel: text += "2 b tag"
    elif 'b' in channel or '1b' in channel: text += "1 b tag"
    elif 'qq' in channel or 'preselection' in channel: text += 'preselection'
    elif 'mumu' in channel or '2mu' in channel: text += '1 #mu'
    elif 'none' in channel: text += 'no selection'
    return text

def drawRegion(channel, left=False, large=False):
    text = getChannel(channel)

    latex = TLatex()
    latex.SetNDC()
    latex.SetTextFont(72) #52
    if large:
        latex.SetTextSize(0.05)
    else:
        latex.SetTextSize(0.04)
    if left: latex.DrawLatex(0.15, 0.79, text)
    else:
        latex.SetTextAlign(22)
        latex.DrawLatex(0.5, 0.85, text)

def drawLine(x1, y1, x2, y2):
    line = TLine(x1, y1, x2, y2)
    line.SetLineStyle(2)
    line.SetLineWidth(2)
    line.Draw()
    return line

def fixData(hist, useGarwood=False, cutGrass=True, maxPoisson=False):
    if hist==None: return
    varBins = ((hist.GetX()[1] - hist.GetX()[0]) != (hist.GetX()[hist.GetN()-1] - hist.GetX()[hist.GetN()-2])) #hist.GetXaxis().IsVariableBinSize()
    avgwidth = (hist.GetX()[hist.GetN()-1]+hist.GetErrorXhigh(hist.GetN()-1) - (hist.GetX()[0]-hist.GetErrorXlow(0))) / hist.GetN()
    alpha = 1 - 0.6827

    for i in list(reversed(range(0, hist.GetN()))):
        width = hist.GetErrorXlow(i) + hist.GetErrorXhigh(i)
        # X error bars to 0 - do not move this, otherwise the first bin will disappear, thanks Wouter and Rene!
        if not varBins:
            hist.SetPointEXlow(i, 0)
            hist.SetPointEXhigh(i, 0)
        # Garwood confidence intervals
        if(useGarwood):
            N = hist.GetY()[i]
            r = width / avgwidth
            if varBins: N = hist.GetY()[i] / r
            N = max(N, 0.) # Avoid unphysical bins
            L = ROOT.Math.gamma_quantile(alpha/2, N, 1.) if N>0 else 0.
            U = ROOT.Math.gamma_quantile_c(alpha/2, N+1, 1)
            # maximum between Poisson and Sumw2 error bars
            EL = N-L if not maxPoisson else max(N-L, hist.GetErrorYlow(i))
            EU = U-N if not maxPoisson else max(U-N, hist.GetErrorYhigh(i))
            hist.SetPointEYlow(i, EL)
            hist.SetPointEYhigh(i, EU)
        # Cut grass
        if cutGrass and hist.GetY()[i] > 0.: cutGrass = False
        # Treatment for 0 bins
        if abs(hist.GetY()[i])<=1.e-6:
            if cutGrass: hist.SetPointError(i, hist.GetErrorXlow(i), hist.GetErrorXhigh(i), 1.e-6, 1.e-6, )
            if (hist.GetX()[i]>65 and hist.GetX()[i]<135 and hist.GetY()[i]==0): hist.SetPointError(i, hist.GetErrorXlow(i), hist.GetErrorXhigh(i), 1.e-6, 1.e-6, )
            hist.SetPoint(i, hist.GetX()[i], -1.e-4)

def bkg_function_plotter(X_mass, m_min, m_max, plot_binning, modelBkg, setData, year, category, chi2, dof, output_file, signal_file=None, signal_workspace=None, signal_norm_factor=1000., n_parameters=""):
    if signal_file is not None:
        assert signal_workspace is not None
    if signal_workspace is not None:
        assert signal_file is not None

    print "starting to plot"
    RATIO = 4 
    if year=='2016':
        #lumi=35920.
        lumi=36330.
    elif year=='2017':
        lumi=41530.
    elif year=='2018':
        lumi=59740.
    elif year=='run2':
        #lumi=137190.
        lumi=137600.

    c = TCanvas("c_"+category, category, 900, 800)
    c.Divide(1, 2)
    setTopPad(c.GetPad(1), RATIO)
    setBotPad(c.GetPad(2), RATIO)
    c.cd(1)
    frame = X_mass.frame()
    setPadStyle(frame, 1.25, True)
    frame.GetXaxis().SetRangeUser(m_min, m_max)

    graphData = setData.plotOn(frame, RooFit.Binning(plot_binning), RooFit.Invisible())
    conversion_factor = 1000/(lumi*graphData.getHist().getNominalBinWidth())

    modelBkg.plotOn(frame, RooFit.LineColor(2), RooFit.DrawOption("L"), RooFit.Normalization(conversion_factor, ROOT.RooAbsReal.Relative), RooFit.Name(modelBkg.GetName()))

    if signal_file is not None:
        m2000_range = (1600., 2200.)
        m4000_range = (3200., 4400.)
        m6000_range = (4800., 6600.)
        X_mass.setRange("signal_m2000", *m2000_range)
        X_mass.setRange("signal_m4000", *m4000_range)
        X_mass.setRange("signal_m6000", *m6000_range)

        if signal_workspace == "bstar":
            signal_norm_2000, signal_pdf_m2000 = extract_signal_histogram(signal_file, "h_qg_2000", X_mass)
            signal_color = 616
            signal_name = "b* Signal m2000"
        else:
            signal_norm_2000, signal_pdf_m2000, _ = extract_workspace(signal_file, signal_workspace,
                "ZpBB_{}_{}_M{}".format(year, category, 2000), options.variable_name, signal=True)
            signal_color = 433
            signal_name = "Z' Signal m2000"

            # correcting height of hist mass point for Z'
            if category=="bb":
                signal_norm_2000 *= 0.3
            elif category=="mumu":
                signal_norm_2000 *= 3.

        graphSignal = signal_pdf_m2000.plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
            RooFit.LineColor(signal_color), RooFit.DrawOption("L"), RooFit.Name(signal_name),
            RooFit.Normalization(signal_norm_factor*signal_norm_2000*conversion_factor, RooAbsReal.NumEvent),
            RooFit.Range("signal_m2000"), RooFit.Binning(plot_binning))
        if signal_workspace == "bstar":
            adjust_bstar_shape(graphSignal.getHist(), m2000_range)

        if signal_workspace == "bstar":
            signal_norm_4000, signal_pdf_m4000 = extract_signal_histogram(signal_file, "h_qg_4000", X_mass)
            signal_color = 617
            signal_name = "b* Signal m4000"
        else:
            signal_norm_4000, signal_pdf_m4000, _ = extract_workspace(signal_file, signal_workspace,
            "ZpBB_{}_{}_M{}".format(year, category, 4000), options.variable_name, signal=True)
            signal_color = 434
            signal_name = "Z' Signal m4000"

        graphSignal = signal_pdf_m4000.plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
            RooFit.LineColor(signal_color), RooFit.DrawOption("L"), RooFit.Name(signal_name),
            RooFit.Normalization(signal_norm_factor*signal_norm_4000*conversion_factor, RooAbsReal.NumEvent),
            RooFit.Range("signal_m4000"), RooFit.Binning(plot_binning))
        if signal_workspace == "bstar":
            adjust_bstar_shape(graphSignal.getHist(), m4000_range)

        if signal_workspace == "bstar":
            signal_norm_6000, signal_pdf_m6000 = extract_signal_histogram(signal_file, "h_qg_6000", X_mass)
            signal_color = 618
            signal_name = "b* Signal m6000"
        else:
            signal_norm_6000, signal_pdf_m6000, _ = extract_workspace(signal_file, signal_workspace,
            "ZpBB_{}_{}_M{}".format(year, category, 6000), options.variable_name, signal=True)
            signal_color = 435
            signal_name = "Z' Signal m6000"

        graphSignal = signal_pdf_m6000.plotOn(frame, RooFit.LineStyle(1), RooFit.LineWidth(2),
            RooFit.LineColor(signal_color), RooFit.DrawOption("L"), RooFit.Name(signal_name),
            RooFit.Normalization(signal_norm_factor*signal_norm_6000*conversion_factor, RooAbsReal.NumEvent),
            RooFit.Range("signal_m6000"), RooFit.Binning(plot_binning))
        if signal_workspace == "bstar":
            adjust_bstar_shape(graphSignal.getHist(), m6000_range)

    graphData = setData.plotOn(frame, RooFit.Binning(plot_binning),
        RooFit.XErrorSize(1), RooFit.DataError(RooAbsData.Poisson),
        RooFit.DrawOption("PE0"), RooFit.Name(setData.GetName()))

    fixData(graphData.getHist(), True, True, False)

    roohist = graphData.getHist()
    for i in range(roohist.GetN()):
        roohist.SetPoint(i, roohist.GetX()[i], conversion_factor*roohist.GetY()[i])
        roohist.SetPointEYlow(i, conversion_factor*roohist.GetEYlow()[i])
        roohist.SetPointEYhigh(i, conversion_factor*roohist.GetEYhigh()[i])

    pulls = frame.pullHist(setData.GetName(), modelBkg.GetName(), True)  
    chi = frame.chiSquare(setData.GetName(), modelBkg.GetName(), True)
    #frame.GetYaxis().SetTitle("Events")
    frame.GetYaxis().SetTitle("d#sigma/dm_{jj} (fb/GeV)")
    #frame.GetYaxis().SetTitleOffset(1.05)
    frame.GetYaxis().SetTitleOffset(0.7)
    frame.GetYaxis().SetTitleSize(0.07)
    #frame.GetYaxis().SetLabelSize(0.045)
    frame.Draw()
    frame.SetTitle("")
    
    frame.SetMaximum(frame.GetMaximum()*conversion_factor*10)
    frame.SetMinimum(2*1e-5)
    c.GetPad(1).SetLogy()

    #drawAnalysis(category)
    drawRegion(category, True, large=True)
    drawCMS(lumi, "", suppress_year=True if year=="run2" else False, large=True)

    leg = TLegend(0.55, 0.6, 0.925, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)

    # ridiculous workaround to retain control over marker in legend
    fake_hist = ROOT.TH1D("fake_hist", "fake_hist", 10, 0, 1) 
    fake_hist.SetMarkerStyle(8)
    fake_hist.SetMarkerColor(1)
    fake_hist.SetLineColor(1)
    fake_hist.Draw("SAME, E1")

    leg.AddEntry(fake_hist.GetName(), "Data", "PEL")
    #leg.AddEntry(setData.GetName(), "Data", "PEL")
    leg.AddEntry(modelBkg.GetName(), modelBkg.GetTitle() if n_parameters=="" else "Fit ({} par.)".format(n_parameters), "L")#.SetTextColor(629)
    if signal_file is not None:
        if signal_workspace=="bstar":
            leg.AddEntry("b* Signal m2000", "b*, m=2000 GeV", "L")
            leg.AddEntry("b* Signal m4000", "b*, m=4000 GeV", "L")
            leg.AddEntry("b* Signal m6000", "b*, m=6000 GeV", "L")
        else:
            leg.AddEntry("Z' Signal m2000", "Z', m=2000 GeV", "L")
            leg.AddEntry("Z' Signal m4000", "Z', m=4000 GeV", "L")
            leg.AddEntry("Z' Signal m6000", "Z', m=6000 GeV", "L")
    leg.SetY1(0.9-leg.GetNRows()*0.075)
    leg.Draw()

    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextFont(42)

    text = TLatex()
    text.SetTextColor(1)
    text.SetTextFont(42)
    text.SetTextAlign(11)
    #text.SetTextSize(0.04)
    text.SetTextSize(0.06)
    text.DrawLatexNDC(0.15, 0.18, "#splitline{#splitline{#chi^{2}/ndf = %.1f/%.0f}{Wide PF-jets}}{#splitline{m_{jj} > 1.53 TeV, |#Delta#eta| < 1.1}{|#eta| < 2.5, p_{T} > 30 GeV}}" % (chi2, dof))
    text.Draw("SAME")

    c.cd(2)
    frame_res = X_mass.frame()
    setPadStyle(frame_res, 1.25)
    frame_res.addPlotable(pulls, "P")
    setBotStyle(frame_res, RATIO, False)
    frame_res.GetXaxis().SetRangeUser(m_min, m_max)
    frame_res.GetYaxis().SetRangeUser(-3, 3)
    frame_res.GetYaxis().SetTitle("Pulls (#sigma)")
    frame_res.GetYaxis().SetTitleOffset(0.21)
    frame_res.GetXaxis().SetTitleOffset(0.9)
    frame_res.SetTitle("")
    frame_res.GetYaxis().SetTitleSize(0.2)   
    frame_res.GetXaxis().SetTitleSize(0.2)
    frame_res.GetXaxis().SetLabelSize(0.17)
    frame_res.Draw()
    fixData(pulls, False, True, False)

    line = drawLine(m_min, 0, m_max, 0)
    c.SaveAs(output_file)

X_MIN = 1530
X_MAX = 7800 #8200

dijet_bins = [1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176, 197, 220, 244, 270, 296, 325, 354, 386, 419, 453, 489, 526, 565, 606, 649, 693, 740, 788, 838, 890, 944, 1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060, 7320, 7589, 7866, 8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430, 10798, 11179, 11571, 11977, 12395, 12827, 13272, 13732, 14000]

bins = [x for x in dijet_bins if x>=X_MIN and x<=X_MAX]
X_min = min(bins)
X_max = max(bins)
abins = array( 'd', bins )
plot_binning = RooBinning(len(abins)-1, abins)

setData, modelBkg, X_mass = extract_workspace(options.input, options.workspace_name, options.model_name,
    options.variable_name, data_name=options.data_name, data_inside=options.external_data_hist=="")

if options.external_data_hist!="":
    test_input_file = ROOT.TFile.Open(options.external_data_hist)
    test_hist = test_input_file.Get(options.data_name)
    setData = ROOT.RooDataHist("data_obs", "data_obs", ROOT.RooArgList(X_mass), ROOT.RooFit.Import(test_hist))

if options.signal_input=="":
    signal_file = None
    signal_workspace = None
else:
    signal_file = options.signal_input
    signal_workspace = options.signal_workspace

bkg_function_plotter(X_mass, X_min, X_max, plot_binning, modelBkg, setData, options.year,
    options.category, options.chi, options.dof, options.output, signal_file=signal_file,
    signal_workspace=signal_workspace, signal_norm_factor=options.signal_norm_factor,
    n_parameters=options.parameters)


