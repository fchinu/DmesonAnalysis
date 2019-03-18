#*************************************************************************************************************#
# python script for the computation of the D+ and Ds+ efficiency mesons from ProjectDplusDsSparse.py output   #
# run: python cutSetFileName.yml inputFileName.root outFileName.root                                          #
# author: Fabrizio Grosa, fabrizio.grosa@to.infn.it ,INFN Torino                                              #
#*************************************************************************************************************#

from ROOT import TFile, TCanvas, TH1F, TLegend # pylint: disable=import-error,no-name-in-module
from ROOT import gROOT, gStyle, kRed, kBlue, kFullCircle, kOpenSquare # pylint: disable=import-error,no-name-in-module
import yaml, sys, array, math

def ComputeEfficiency(recoCounts, genCounts):
    hTmpNum = TH1F('hTmpNum', '', 1,0,1)
    hTmpDen = TH1F('hTmpDen', '', 1,0,1)
    hTmpNum.SetBinContent(1, recoCounts)
    hTmpDen.SetBinContent(1, genCounts)
    hTmpNum.Sumw2()
    hTmpDen.Sumw2()
    hTmpNum.Divide(hTmpNum,hTmpDen,1.,1,'B')
    return hTmpNum.GetBinContent(1), hTmpNum.GetBinError(1)

def SetHistoStyle(histo, color, marker, markersize=1.5, linewidth=2, linestyle=1):
    histo.SetMarkerColor(color)
    histo.SetLineColor(color)
    histo.SetLineStyle(linestyle)
    histo.SetLineWidth(linewidth)
    histo.SetMarkerStyle(marker)
    histo.SetMarkerSize(markersize)

cutSetFileName = sys.argv[1]
inFileName = sys.argv[2]
outFileName = sys.argv[3]

with open(cutSetFileName, 'r') as ymlcutSetFile:
    cutSet = yaml.load(ymlcutSetFile)

PtMin = cutSet['cutvars']['Pt']['min']
PtMax = cutSet['cutvars']['Pt']['max']
cutSet['cutvars']['Pt']['limits'] = list(cutSet['cutvars']['Pt']['min'])
cutSet['cutvars']['Pt']['limits'].append(cutSet['cutvars']['Pt']['max'][len(cutSet['cutvars']['Pt']['max'])-1])
nPtBins = len(PtMin)

hEffPrompt = TH1F('hEffPrompt',';#it{p}_{T} (GeV/#it{c});Efficiency',nPtBins,array.array('f',cutSet['cutvars']['Pt']['limits']))
hEffFD = TH1F('hEffFD',';#it{p}_{T} (GeV/#it{c});Efficiency',nPtBins,array.array('f',cutSet['cutvars']['Pt']['limits']))
SetHistoStyle(hEffPrompt,kRed,kFullCircle)
SetHistoStyle(hEffFD,kBlue,kOpenSquare,1.5,2,7)

hRecoPrompt, hRecoFD, hGenPrompt, hGenFD = ([] for iHisto in range(4))

infile = TFile(inFileName)
for iPt in range(len(PtMin)):
    hRecoPrompt.append(infile.Get('hPromptPt_%0.f_%0.f' % (PtMin[iPt], PtMax[iPt])))
    hRecoFD.append(infile.Get('hFDPt_%0.f_%0.f' % (PtMin[iPt], PtMax[iPt])))
    hGenPrompt.append(infile.Get('hPromptGenPt_%0.f_%0.f' % (PtMin[iPt], PtMax[iPt])))
    hGenFD.append(infile.Get('hFDGenPt_%0.f_%0.f' % (PtMin[iPt], PtMax[iPt])))
    effPrompt, effPromptUnc = ComputeEfficiency(hRecoPrompt[iPt].Integral(),hGenPrompt[iPt].Integral())
    effFD, effFDUnc = ComputeEfficiency(hRecoFD[iPt].Integral(),hGenFD[iPt].Integral())
    hEffPrompt.SetBinContent(iPt+1,effPrompt)
    hEffPrompt.SetBinError(iPt+1,effPromptUnc)
    hEffFD.SetBinContent(iPt+1,effFD)
    hEffFD.SetBinError(iPt+1,effFDUnc)

gStyle.SetPadRightMargin(0.035)
gStyle.SetPadLeftMargin(0.14)
gStyle.SetPadTopMargin(0.035)
gStyle.SetTitleSize(0.045,'xy')
gStyle.SetLabelSize(0.040,'xy')
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)
gStyle.SetLegendBorderSize(0)
gStyle.SetOptStat(0)

leg = TLegend(0.2,0.6,0.4,0.8)
leg.SetTextSize(0.045)
leg.SetFillStyle(0)
leg

hEffPrompt.SetDirectory(0)
hEffFD.SetDirectory(0)
cEff = TCanvas('cEff','',800,800)
cEff.DrawFrame(PtMin[0],1.e-5,PtMax[nPtBins-1],1.,';#it{p}_{T} (GeV/#it{c});Efficiency;')
cEff.SetLogy()
hEffPrompt.Draw('same')
hEffFD.Draw('same')

cEff.SaveAs("test.pdf")
raw_input('Press enter to exit')
