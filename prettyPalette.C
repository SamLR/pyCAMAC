/**
 * Root macro to set a prettier palette than the default one
 * Just do .x prettyPalette.C from the CINT to set it up
 *
 */

void prettyPalette(){
  
  const Int_t NCont = 99;
  
  const Int_t NRGBs = 5;
  Double_t stops[NRGBs] = { 0.00, 0.34, 0.61, 0.84, 1.00 };
  Double_t red[NRGBs]   = { 0.00, 0.00, 0.87, 1.00, 0.51 };
  Double_t green[NRGBs] = { 0.00, 0.81, 1.00, 0.20, 0.00 };
  Double_t blue[NRGBs]  = { 0.51, 1.00, 0.12, 0.00, 0.00 };
   
 /*
  const Int_t NRGBs = 10;
  Double_t stops[NRGBs] = { 0.00, 0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 0.77, 0.88, 1.00 };
  Double_t red[NRGBs]   = { 0.00, 0.00, 0.00, 0.00, 0.20, 0.90, 0.95, 0.96, 0.92, 0.80 };
  Double_t green[NRGBs] = { 0.00, 0.00, 0.50, 0.81, 0.90, 0.90, 1.00, 0.60, 0.20, 0.00 };
  Double_t blue[NRGBs]  = { 0.20, 0.90, 0.95, 1.00, 0.70, 0.10, 0.02, 0.00, 0.00, 0.00 };
  */
  TColor::CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
  gStyle->SetNumberContours(NCont);
}
