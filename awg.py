from CoolProp.HumidAirProp import HAPropsSI as airprop
from CoolProp.CoolProp import PropsSI as satprop


def vcr(Tcool=10, delta_T=8.0, Ref='R407c'):
    '''Takes in the Coil temperature, Heat exchanger(s) temperature difference and Refrigerant type as input;
    Returns the specific heat and work of the compressor, condenser and evaporator'''

    TH = Tcool + 273.15 + delta_T  # Refrigerant Temperature in Condenser (Assume cool air from evaporator)
    TC = Tcool + 273.15 - delta_T  # Refrigerant Temperature in Evaporator
    LP = satprop('P', 'T', TC, 'Q', 1, Ref)  # Saturation pressure at TC
    HP = satprop('P', 'T', TH, 'Q', 1, Ref)  # Saturation pressure at TH

    # After Evaporator
    h1 = satprop('H', 'P', LP, 'Q', 1, Ref)
    s1 = satprop('S', 'P', LP, 'Q', 1, Ref)
    T1 = satprop('T', 'P', LP, 'Q', 1, Ref)

    # After Compressor
    n = 0.72
    h2s = satprop('H', 'P', HP, 'S', s1, Ref)  # Isentropic
    h2 = h1 + (h2s - h1) / n
    T2 = satprop('T', 'P', HP, 'H', h2, Ref)

    # After Condenser
    h3 = satprop('H', 'P', HP, 'Q', 0, Ref)
    T3 = satprop('T', 'P', HP, 'Q', 1, Ref)
    s3 = satprop('T', 'P', HP, 'Q', 1, Ref)

    # After Expansion valve
    h4 = h3
    hf4 = satprop('H', 'P', LP, 'Q', 0, Ref)
    hg4 = h1
    x4 = (h4 - hf4) / (hg4 - hf4)

    qevap = (h1 - h4)  # Specific Evaporator heat input
    wcomp = (h2 - h1)  # Specific Compressor work input
    qcond = (h3 - h2)  # Specific Condenser heat output

    return wcomp, qcond, qevap


def awg(Tamb=26.7, Tcoil=10, RH=0.60, Pres=101325.0, Ref='R407c', AirDrop=500):
    '''Takes in the Ambient conditions (Temperature, Humidity and Pressure), Refrigerant and Machine type as Input;
    Returns produced water, Required a flowrate of air'''
    T1 = Tamb + 273.15  # Air temperature before cooling down
    T2 = Tcoil + 273.15  # Air temperature after cooling
    mw_max = AirDrop / (24 * 3600)  # Convert the maximum produced water kg per second

    #     Humidity ratio
    w_std = airprop('Omega', 'T', 25 + 273.15, 'P', Pres, 'R',
                    0.575)  # Standard humidity ratio for 25°C, atmospheric pressure and 57.5% relative humidity
    w1 = airprop('Omega', 'T', T1, 'P', Pres, 'R', RH)  # Humidity ratio for air entry
    w2 = airprop('Omega', 'T', T2, 'P', Pres, 'R', 1)  # Humidity ratio for air exit

    #     Dry air enthalpy
    ha1 = airprop('H', 'T', T1, 'P', Pres, 'R', RH)  # Entry
    ha2 = airprop('H', 'T', T2, 'P', Pres, 'R', 1)  # Exit

    #     Saturated water properties (Q=0: Liquid)
    hg1 = satprop('H', 'T', T1, 'Q', 1, 'IF97::Water')  # Vapor water (entry)
    hg2 = satprop('H', 'T', T2, 'Q', 1, 'IF97::Water')  # Vapor water (exit)
    hf2 = satprop('H', 'T', T2, 'Q', 0, 'IF97::Water')  # Liquid water (exit)

    mt_req = mw_max * (
                1 + 1 / w_std)  # Total amount of humid air required to generate the standard amount of water (kg/s)
    ma_req = mt_req - mw_max  # Mass of dry air required
    q_evap_unit = vcr(Tcool=10, Ref=Ref)[2]  # speicific enthalpy change at the evaporator (KJ/kg)
    q_cv = ((ha2 - ha1) - w1 * hg1 + w2 * hg2 + (w1 - w2) * hf2)  # control volume heat flow

    w_comp, q_cond, q_evap = vcr(Tcool=Tcoil,
                                 Ref=Ref)  # specific heat and work for vcr unit based on cooling temperature
    mr_per_air = q_cv / -q_evap  # Required refrigerant amount per unit air
    mr_req = ma_req * mr_per_air  # required refrigerant flow rate

    Q_evap_eff = mr_req * q_evap  # Heat flow (W)
    Q_cond_eff = mr_req * q_cond
    W_comp_eff = mr_req * w_comp  # Work input (W)
    ma_eff = Q_evap_eff / -q_cv  # Mass flowrate of air

    mw_eff = ma_eff * (w1 - w2)
    mt_eff = ma_eff + mw_eff
    # hw = (w1-w2)*hf2
    D_w = satprop('D', 'T', T2, 'Q', 0, 'IF97::Water')  # Density of water vapor
    D_air = 1 / airprop('Vha', 'T', T1, 'P', Pres, 'R', RH)  # Density of air
    water_flow = (3600 * 1000 * mw_eff / D_w)  # Water produced (liter per hour)
    air_flow = mt_req * 3600 / D_air  # Air required to produce water

    return water_flow, W_comp_eff / 1000