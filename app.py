from flask import Flask, render_template, request, session, redirect, url_for
import csv, os, uuid, json, math
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'epistemic_alignment_conditionA_2024'

# ── 30 UNIQUE COMPANY NAMES — never repeated ─────────────────────────────────
# 2 unique companies per round × 15 rounds = 30 total

ALL_ROUNDS = {
    "Information Technology": [
        (1,  "Nexora Systems",    142.50, 3.8,  1.5, "Dataflux Inc",      87.20,  2.1,  1.8),
        (2,  "CloudPeak Corp",    156.80, 4.5,  1.6, "ByteWave Ltd",      94.40,  11.2, 2.2),
        (3,  "QuantumBridge Inc", 203.60, 3.1,  1.9, "PixelStream Corp",  118.90, 9.8,  2.1),
        (4,  "CipherCore Ltd",    178.30, 7.8,  1.7, "SoftNova Inc",      132.60, 3.4,  2.0),
        (5,  "GridLogic Corp",    145.20, 5.5,  1.5, "VaultTech Ltd",     159.40, 10.2, 1.8),
        (6,  "NeuralPath Inc",    97.30,  8.9,  2.3, "CodeSpire Corp",    198.70, 4.1,  1.9),
        (7,  "DataSphere Ltd",    122.50, 6.7,  2.0, "SyncWave Inc",      181.90, 3.5,  1.7),
        (8,  "ByteForge Corp",    89.60,  9.1,  1.8, "PulseNet Ltd",      135.80, 4.2,  2.1),
        (9,  "CoreMatrix Inc",    147.80, 5.8,  1.6, "TechSpan Corp",     201.30, 3.3,  1.9),
        (10, "InfiniteLoop Ltd",  162.10, 4.4,  1.7, "NodeBridge Inc",    184.20, 8.7,  2.2),
        (11, "AlphaGrid Corp",    99.80,  7.6,  2.0, "SignalBase Ltd",    125.30, 3.9,  1.8),
        (12, "OmegaStack Inc",    138.40, 5.2,  1.9, "ProtoCore Corp",    149.90, 9.5,  1.6),
        (13, "ZenithTech Ltd",    204.70, 3.8,  2.1, "ApexFlow Inc",      91.20,  7.1,  1.7),
        (14, "VectorNet Corp",    186.50, 8.3,  1.8, "PrismData Ltd",     102.10, 4.6,  2.3),
        (15, "HelixSoft Inc",     152.30, 10.8, 1.5, "TerraLogic Corp",   127.80, 3.9,  2.0),
    ],
    "Health Care": [
        (1,  "MediVance Corp",    198.30, 4.2,  1.6, "CurePoint Ltd",     134.60, 9.8,  2.0),
        (2,  "BioNexus Inc",      245.80, 3.5,  1.8, "HealthBridge Corp", 89.40,  11.4, 2.3),
        (3,  "PharmaPeak Ltd",    312.60, 8.7,  1.7, "WellPath Inc",      167.90, 3.2,  1.9),
        (4,  "ClinixCore Corp",   138.20, 5.1,  2.0, "GenoBridge Ltd",    249.30, 9.1,  1.8),
        (5,  "VitalStream Inc",   92.40,  10.3, 2.1, "MedixCore Corp",    308.70, 4.5,  1.7),
        (6,  "PharmaLink Ltd",    201.50, 3.8,  1.9, "BioVault Inc",      171.20, 8.6,  2.2),
        (7,  "NovaCure Corp",     252.10, 6.9,  1.6, "HealthSpan Ltd",    141.40, 3.7,  2.0),
        (8,  "CellBridge Inc",    315.40, 4.3,  2.1, "GenePeak Corp",     95.80,  10.2, 1.8),
        (9,  "MediCore Ltd",      174.60, 7.8,  1.7, "BioStream Inc",     204.20, 3.4,  2.1),
        (10, "LifePath Corp",     144.30, 3.6,  2.0, "PharmaVault Ltd",   318.90, 9.7,  1.9),
        (11, "CureStream Inc",    98.60,  8.4,  1.8, "MediBridge Corp",   255.40, 4.1,  2.2),
        (12, "BioLink Ltd",       207.80, 5.7,  2.1, "VitalCore Inc",     322.10, 10.5, 1.6),
        (13, "HealthNova Corp",   177.30, 3.9,  1.9, "ClinixStream Ltd",  147.60, 8.2,  2.0),
        (14, "GenoBridge Inc",    258.70, 9.3,  1.7, "MediVault Corp",    211.40, 4.8,  1.8),
        (15, "PharmaPulse Ltd",   325.80, 4.6,  2.0, "BioCore Inc",       101.90, 11.1, 2.3),
    ],
    "Energy": [
        (1,  "SolarNexus Corp",   156.40, 8.9,  1.7, "PetroVance Ltd",    203.20, 3.6,  2.0),
        (2,  "GreenPeak Inc",     89.30,  10.4, 2.1, "PowerBridge Corp",  134.80, 4.2,  1.8),
        (3,  "OilStream Ltd",     267.50, 3.8,  1.9, "EnergyCore Inc",    158.90, 9.7,  2.2),
        (4,  "FuelVault Corp",    206.80, 7.6,  1.6, "WindPath Ltd",      92.40,  3.5,  1.9),
        (5,  "SolarBridge Inc",   137.60, 9.2,  2.0, "GasLink Corp",      264.30, 4.8,  1.7),
        (6,  "TerraFuel Ltd",     161.20, 4.1,  1.8, "HydroNexus Inc",    95.80,  10.6, 2.1),
        (7,  "PowerStream Corp",  210.40, 8.3,  1.7, "CoalVault Ltd",     140.50, 3.7,  2.0),
        (8,  "NuclearBridge Inc", 261.80, 5.9,  2.2, "SolarCore Corp",    213.70, 9.4,  1.8),
        (9,  "WindStream Ltd",    163.90, 4.5,  1.9, "GreenBridge Inc",   143.20, 10.8, 2.3),
        (10, "EcoFuel Corp",      99.20,  7.8,  1.6, "PetroLink Ltd",     259.40, 3.9,  2.0),
        (11, "HydroPath Inc",     146.30, 9.6,  2.1, "SolarVault Corp",   167.10, 4.3,  1.7),
        (12, "GasPeak Ltd",       217.60, 3.7,  1.8, "WindCore Inc",      102.50, 10.2, 2.2),
        (13, "BiofuelBridge Corp",257.20, 8.1,  1.9, "PowerNexus Ltd",    149.40, 4.6,  2.0),
        (14, "TerraStream Inc",   170.80, 4.8,  1.7, "FuelCore Corp",     221.30, 9.9,  1.8),
        (15, "EnergyVault Ltd",   105.90, 10.7, 2.3, "GreenStream Inc",   174.20, 3.4,  1.9),
    ],
    "Financials": [
        (1,  "CapitalNexus Corp", 312.40, 4.8,  1.7, "WealthBridge Ltd",  187.60, 9.6,  2.0),
        (2,  "BankStream Inc",    156.80, 9.2,  1.8, "InvestCore Corp",   234.50, 4.1,  1.9),
        (3,  "FinVault Ltd",      289.30, 3.9,  2.1, "TrustPeak Inc",     315.70, 10.4, 1.7),
        (4,  "CreditBridge Corp", 191.20, 8.7,  1.6, "AssetStream Ltd",   159.40, 3.6,  2.2),
        (5,  "WealthNexus Inc",   238.80, 5.3,  2.0, "EquityCore Corp",   286.10, 9.8,  1.8),
        (6,  "MoneyPath Ltd",     318.90, 4.2,  1.9, "FundBridge Inc",    242.30, 10.7, 2.1),
        (7,  "TrustStream Corp",  162.60, 7.9,  1.7, "BankVault Ltd",     194.80, 3.8,  1.9),
        (8,  "InvestLink Inc",    283.40, 9.4,  2.2, "CapitalCore Corp",  246.10, 4.5,  1.8),
        (9,  "AssetNexus Ltd",    322.50, 3.7,  1.8, "WealthStream Inc",  165.30, 10.1, 2.0),
        (10, "EquityBridge Corp", 198.60, 8.3,  1.9, "FinCore Ltd",       281.20, 4.9,  1.7),
        (11, "FundNexus Inc",     249.80, 5.6,  2.1, "CreditStream Corp", 326.40, 9.3,  2.2),
        (12, "MoneyCore Ltd",     168.20, 4.1,  1.8, "TrustLink Inc",     279.30, 10.8, 1.9),
        (13, "BankPath Corp",     202.40, 9.7,  1.7, "InvestVault Ltd",   253.20, 3.5,  2.0),
        (14, "CapitalStream Inc", 277.50, 3.8,  2.3, "WealthCore Corp",   171.60, 8.9,  1.8),
        (15, "FinBridge Ltd",     330.20, 10.2, 1.6, "AssetLink Inc",     206.80, 4.4,  2.1),
    ],
    "Consumer Discretionary": [
        (1,  "RetailNexus Corp",  234.50, 9.4,  1.8, "ShopStream Ltd",    156.80, 3.7,  2.1),
        (2,  "BrandCore Inc",     189.30, 4.2,  1.9, "MarketVault Corp",  98.40,  10.6, 2.0),
        (3,  "StyleBridge Ltd",   312.60, 3.6,  2.2, "TrendLink Inc",     237.20, 9.1,  1.7),
        (4,  "LuxuryStream Corp", 160.40, 8.8,  1.6, "FashionCore Ltd",   192.80, 4.5,  2.3),
        (5,  "RetailVault Inc",   101.30, 10.3, 2.1, "BrandStream Corp",  309.40, 3.8,  1.8),
        (6,  "ShopNexus Ltd",     239.80, 4.9,  1.9, "MarketCore Inc",    104.60, 9.7,  2.0),
        (7,  "StyleStream Corp",  196.20, 7.6,  1.7, "TrendVault Ltd",    163.90, 3.4,  2.2),
        (8,  "LuxuryCore Inc",    306.80, 9.2,  2.0, "FashionLink Corp",  107.40, 4.8,  1.9),
        (9,  "RetailPath Ltd",    242.50, 4.3,  1.8, "BrandVault Inc",    199.60, 10.9, 2.1),
        (10, "ShopBridge Corp",   167.30, 8.7,  1.9, "MarketStream Ltd",  304.20, 3.6,  1.7),
        (11, "StyleNexus Inc",    110.80, 5.4,  2.2, "TrendCore Corp",    245.30, 9.4,  2.0),
        (12, "LuxuryLink Ltd",    203.10, 3.9,  1.8, "FashionVault Inc",  301.80, 8.1,  2.3),
        (13, "RetailCore Corp",   170.60, 10.1, 1.7, "BrandPath Ltd",     114.20, 4.2,  1.9),
        (14, "ShopStream Inc",    299.50, 4.7,  2.1, "MarketLink Corp",   206.80, 9.8,  1.8),
        (15, "StyleVault Ltd",    248.40, 8.4,  1.9, "TrendStream Inc",   174.10, 3.7,  2.0),
    ],
    "Consumer Staples": [
        (1,  "GroceryNexus Corp", 178.60, 4.1,  1.5, "FoodStream Ltd",    234.30, 9.3,  1.8),
        (2,  "HouseholdCore Inc", 145.20, 9.7,  1.7, "StapleVault Corp",  189.70, 3.8,  2.0),
        (3,  "FoodBridge Ltd",    180.40, 3.5,  1.6, "GroceryCore Inc",   147.80, 10.4, 2.1),
        (4,  "StapleStream Corp", 237.10, 8.9,  1.8, "HouseholdLink Ltd", 192.40, 4.2,  1.9),
        (5,  "FoodNexus Inc",     150.30, 10.1, 2.0, "GroceryVault Corp", 182.80, 3.6,  1.7),
        (6,  "StapleBridge Ltd",  195.20, 4.6,  1.9, "HouseholdCore Inc", 184.90, 9.8,  2.2),
        (7,  "FoodVault Corp",    239.80, 7.3,  1.6, "GroceryLink Ltd",   153.10, 3.9,  2.0),
        (8,  "StapleCore Inc",    187.30, 9.4,  1.8, "HouseholdStream Corp",198.00,4.7, 1.7),
        (9,  "FoodPath Ltd",      156.40, 3.7,  2.1, "GroceryStream Inc", 242.60, 10.6, 1.9),
        (10, "StapleNexus Corp",  201.20, 8.2,  1.7, "HouseholdVault Ltd",190.10, 4.1,  2.0),
        (11, "FoodCore Inc",      192.60, 4.9,  1.9, "GroceryPath Corp",  159.20, 9.7,  2.1),
        (12, "StapleStream Ltd",  245.80, 10.3, 1.6, "HouseholdNexus Inc",204.40, 3.5,  1.8),
        (13, "FoodLink Corp",     162.30, 3.8,  2.0, "GroceryBridge Ltd", 195.20, 8.9,  2.2),
        (14, "StaplePath Inc",    208.10, 9.6,  1.7, "HouseholdCore Corp",248.90, 4.3,  1.9),
        (15, "FoodStream Ltd",    198.10, 4.4,  1.8, "GroceryNova Inc",   165.80, 10.8, 2.3),
    ],
    "Industrials": [
        (1,  "AeroNexus Corp",    287.40, 9.1,  1.7, "ManufactureCore Ltd",198.60,3.8,  2.0),
        (2,  "TransportStream Inc",156.80,4.6,  1.9, "IndustryVault Corp",234.20, 10.3, 1.8),
        (3,  "BuildNexus Ltd",    312.50, 3.7,  2.1, "AeroBridge Corp",   291.30, 9.7,  1.7),
        (4,  "ManufactureLink Inc",201.40,8.4,  1.6, "TransportCore Ltd", 159.60, 4.1,  2.2),
        (5,  "IndustryStream Corp",237.80,10.6, 2.0, "BuildCore Inc",     309.20, 3.5,  1.9),
        (6,  "AeroVault Ltd",     294.80, 4.8,  1.8, "ManufactureNexus Corp",241.30,9.2,2.1),
        (7,  "TransportBridge Inc",162.40,7.3,  1.7, "IndustryCore Ltd",  204.80, 4.6,  1.9),
        (8,  "BuildStream Corp",  306.80, 9.8,  2.2, "AeroLink Inc",      244.60, 3.7,  1.8),
        (9,  "ManufactureVault Ltd",298.20,4.2, 1.9, "TransportNexus Corp",165.30,10.4, 2.0),
        (10, "IndustryBridge Inc",208.20, 8.7,  1.7, "BuildVault Ltd",    304.50, 4.9,  2.1),
        (11, "AeroStream Corp",   247.80, 3.9,  2.0, "ManufactureCore Inc",302.10,9.6,  1.8),
        (12, "TransportVault Ltd",168.20, 10.1, 1.9, "IndustryLink Corp", 211.60, 3.4,  2.2),
        (13, "BuildBridge Inc",   302.30, 4.7,  1.8, "AeroCore Ltd",      251.20, 8.9,  1.7),
        (14, "ManufactureStream Corp",305.90,9.3,1.7,"TransportLink Inc", 171.50, 4.2,  2.0),
        (15, "IndustryNexus Ltd", 215.00, 3.8,  2.1, "BuildStream Corp",  300.10, 10.7, 1.9),
    ],
    "Materials": [
        (1,  "ChemNexus Corp",    156.40, 8.6,  1.8, "MiningCore Ltd",    234.80, 3.9,  2.1),
        (2,  "PackageStream Inc", 89.30,  4.3,  1.9, "MaterialVault Corp",178.60, 10.2, 1.7),
        (3,  "ChemBridge Ltd",    158.90, 3.7,  2.0, "MiningLink Inc",    92.10,  9.4,  2.2),
        (4,  "PackageCore Corp",  237.60, 9.1,  1.7, "MaterialStream Ltd",181.40, 4.6,  1.9),
        (5,  "ChemVault Inc",     94.80,  10.5, 2.1, "MiningVault Corp",  161.40, 3.8,  1.8),
        (6,  "PackageNexus Ltd",  184.20, 4.8,  1.9, "MaterialCore Inc",  163.80, 9.7,  2.0),
        (7,  "ChemStream Corp",   240.40, 7.9,  1.7, "MiningBridge Ltd",  97.60,  4.1,  2.3),
        (8,  "PackageBridge Inc", 166.20, 9.3,  2.0, "MaterialLink Corp", 187.00, 3.6,  1.8),
        (9,  "ChemCore Ltd",      100.30, 4.5,  1.8, "MiningStream Inc",  243.20, 10.8, 2.1),
        (10, "PackagePath Corp",  189.80, 8.7,  1.9, "MaterialBridge Ltd",168.90, 4.3,  1.7),
        (11, "ChemLink Inc",      171.60, 3.9,  2.2, "MiningCore Corp",   103.10, 9.6,  2.0),
        (12, "PackageVault Ltd",  246.30, 10.4, 1.8, "MaterialNexus Inc", 193.00, 4.8,  1.9),
        (13, "ChemPath Corp",     105.80, 4.2,  1.7, "MiningLink Ltd",    174.30, 8.3,  2.1),
        (14, "PackageStream Inc", 196.40, 9.8,  2.0, "MaterialCore Corp", 249.80, 3.7,  1.8),
        (15, "ChemNova Ltd",      177.20, 3.6,  1.9, "MiningVault Inc",   108.60, 10.9, 2.2),
    ],
    "Real Estate": [
        (1,  "PropNexus Corp",    234.60, 4.7,  1.6, "REITStream Ltd",    312.80, 9.3,  1.9),
        (2,  "EstateCore Inc",    178.30, 9.8,  1.8, "PropertyVault Corp",156.40, 3.6,  2.1),
        (3,  "PropBridge Ltd",    237.40, 3.5,  2.0, "REITCore Inc",      181.60, 10.7, 1.7),
        (4,  "EstateStream Corp", 316.20, 8.4,  1.7, "PropertyLink Ltd",  159.30, 4.2,  2.2),
        (5,  "PropVault Inc",     184.90, 10.2, 2.1, "REITBridge Corp",   240.20, 3.8,  1.8),
        (6,  "EstateLink Ltd",    162.10, 4.6,  1.9, "PropertyCore Inc",  243.10, 9.6,  2.0),
        (7,  "PropStream Corp",   319.80, 7.8,  1.7, "REITVault Ltd",     188.30, 4.1,  2.3),
        (8,  "EstateNexus Inc",   246.20, 9.4,  2.0, "PropertyStream Corp",165.00,3.7,  1.8),
        (9,  "PropCore Ltd",      191.60, 3.9,  1.8, "REITLink Inc",      323.40, 10.4, 2.1),
        (10, "EstateBridge Corp", 167.80, 8.9,  1.9, "PropertyNexus Ltd", 249.30, 4.5,  1.7),
        (11, "PropLink Inc",      252.40, 4.3,  2.2, "REITCore Corp",     195.00, 9.8,  2.0),
        (12, "EstateVault Ltd",   327.20, 10.6, 1.7, "PropertyBridge Inc",170.60, 3.5,  1.9),
        (13, "PropStream Corp",   198.30, 4.8,  1.8, "REITPath Ltd",      255.60, 8.7,  2.1),
        (14, "EstateCore Inc",    173.40, 9.1,  2.0, "PropertyVault Corp",331.40, 4.2,  1.8),
        (15, "PropNova Ltd",      258.90, 3.7,  1.9, "REITStream Inc",    201.80, 10.3, 2.2),
    ],
    "Utilities": [
        (1,  "PowerNexus Corp",   134.60, 4.3,  1.4, "UtilityStream Ltd", 189.30, 9.1,  1.7),
        (2,  "ElectricCore Inc",  98.40,  9.6,  1.6, "GasVault Corp",     156.80, 3.8,  1.9),
        (3,  "PowerBridge Ltd",   136.80, 3.7,  1.5, "UtilityCore Inc",   100.90, 10.4, 1.8),
        (4,  "ElectricStream Corp",192.10,8.2,  1.7, "GasLink Ltd",       159.40, 4.1,  2.0),
        (5,  "PowerVault Inc",    103.40, 10.1, 1.9, "UtilityBridge Corp",139.20, 3.6,  1.6),
        (6,  "ElectricLink Ltd",  162.10, 4.6,  1.6, "GasCore Inc",       141.60, 9.7,  1.8),
        (7,  "PowerStream Corp",  195.00, 7.4,  1.5, "UtilityVault Ltd",  105.90, 4.2,  1.9),
        (8,  "ElectricNexus Inc", 144.10, 9.3,  1.7, "GasStream Corp",    164.80, 3.9,  2.1),
        (9,  "PowerCore Ltd",     108.40, 4.8,  1.8, "UtilityLink Inc",   197.90, 10.6, 1.7),
        (10, "ElectricVault Corp",167.60, 8.7,  1.6, "GasNexus Ltd",      146.80, 4.3,  1.9),
        (11, "PowerLink Inc",     149.50, 3.9,  1.7, "UtilityCore Corp",  110.90, 9.4,  2.0),
        (12, "ElectricBridge Ltd",200.80, 10.2, 1.5, "GasVault Inc",      170.40, 4.7,  1.8),
        (13, "PowerStream Corp",  113.40, 4.4,  1.9, "UtilityNexus Ltd",  152.20, 8.8,  1.7),
        (14, "ElectricPath Inc",  173.20, 9.8,  1.6, "GasBridge Corp",    203.70, 3.6,  2.0),
        (15, "PowerNova Ltd",     155.00, 3.7,  1.8, "UtilityStream Inc", 115.90, 10.7, 1.9),
    ],
    "Communication Services": [
        (1,  "MediaNexus Corp",   267.40, 9.4,  1.8, "TelecomCore Ltd",   198.60, 3.7,  2.1),
        (2,  "StreamVault Inc",   134.80, 4.1,  1.9, "CommBridge Corp",   312.40, 10.2, 1.7),
        (3,  "MediaCore Ltd",     270.20, 3.6,  2.0, "TelecomStream Inc", 137.60, 9.8,  2.2),
        (4,  "StreamLink Corp",   201.40, 8.7,  1.7, "CommVault Ltd",     315.80, 4.3,  1.9),
        (5,  "MediaBridge Inc",   140.50, 10.3, 2.1, "TelecomNexus Corp", 273.10, 3.8,  1.8),
        (6,  "StreamCore Ltd",    319.20, 4.8,  1.8, "CommStream Inc",    276.00, 9.6,  2.0),
        (7,  "MediaVault Corp",   204.30, 7.6,  1.7, "TelecomLink Ltd",   143.40, 4.1,  2.3),
        (8,  "StreamNexus Inc",   278.90, 9.2,  2.0, "CommCore Corp",     322.60, 3.9,  1.8),
        (9,  "MediaLink Ltd",     146.30, 4.4,  1.9, "TelecomVault Inc",  207.20, 10.7, 2.1),
        (10, "StreamBridge Corp", 326.00, 8.8,  1.7, "CommNexus Ltd",     281.80, 4.6,  1.9),
        (11, "MediaStream Inc",   284.70, 3.7,  2.2, "TelecomCore Corp",  149.20, 9.3,  2.0),
        (12, "StreamVault Ltd",   210.10, 10.4, 1.8, "CommLink Inc",      329.40, 4.8,  1.7),
        (13, "MediaNova Corp",    152.10, 4.2,  1.9, "TelecomBridge Ltd", 287.60, 8.7,  2.1),
        (14, "StreamCore Inc",    332.80, 9.7,  1.7, "CommVault Corp",    213.40, 3.5,  1.9),
        (15, "MediaPath Ltd",     290.50, 3.9,  2.0, "TelecomStream Corp",155.00, 10.8, 2.2),
    ],
}

def generate_trajectory(start_price, growth_6m_pct, volatility, seed):
    """Generate 126 daily prices using GBM model"""
    import random
    random.seed(seed)
    days = 126
    daily_drift = (growth_6m_pct / 100) / days
    daily_vol   = (volatility / 100)
    prices = [start_price]
    for _ in range(days):
        r = random.gauss(daily_drift, daily_vol)
        prices.append(round(prices[-1] * (1 + r), 2))
    return prices

def get_final_change(start, growth_pct):
    end = start * (1 + growth_pct/100)
    change = ((end - start) / start) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%", end

def get_phase(rnd):
    if rnd <= 5:  return 1
    if rnd <= 10: return 2
    return 3

def build_ai_text(rnd, sa, sb, goal, risk, hold, rd):
    phase = get_phase(rnd)
    if phase == 1:
        return (
            f"Based on your <strong>{goal}</strong> investment goal, "
            f"your <strong>{risk}</strong> risk preference, and your "
            f"<strong>{hold}</strong> hold duration — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"are suitable for your portfolio this round."
        )
    elif phase == 2:
        allocs = [float(rd.get(f'R{r}_alloc', 50)) for r in range(1,6)]
        confs  = [float(rd.get(f'R{r}_conf',  50)) for r in range(1,6)]
        avg_slider = sum(allocs)/len(allocs) if allocs else 50
        avg_a   = round(avg_slider * 10)
        avg_b   = 1000 - avg_a
        avg_conf= round(sum(confs)/len(confs), 1) if confs else 50.0
        return (
            f"Based on your <strong>{goal}</strong> investment goal, "
            f"your <strong>{risk}</strong> risk preference, your "
            f"<strong>{hold}</strong> hold duration, and your recent "
            f"investment pattern — averaging <strong>${avg_a}</strong> "
            f"toward Stock A and <strong>${avg_b}</strong> toward Stock B "
            f"with <strong>{avg_conf}%</strong> average confidence — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"are suitable for your portfolio this round."
        )
    else:
        allocs = [float(rd.get(f'R{r}_alloc', 50)) for r in range(1,11)]
        confs  = [float(rd.get(f'R{r}_conf',  50)) for r in range(1,11)]
        acis   = [abs(float(rd.get(f'R{r}_alloc',50))-50)*2/100 for r in range(1,11)]
        avg_slider = sum(allocs)/len(allocs) if allocs else 50
        avg_a   = round(avg_slider * 10)
        avg_b   = 1000 - avg_a
        avg_conf= round(sum(confs)/len(confs), 1) if confs else 50.0
        avg_aci = round(sum(acis)/len(acis), 2) if acis else 0.0
        return (
            f"Based on your <strong>{goal}</strong> investment goal, "
            f"your <strong>{risk}</strong> risk preference, your "
            f"<strong>{hold}</strong> hold duration, and your consistent "
            f"investment pattern across 10 rounds — averaging "
            f"<strong>${avg_a}</strong> toward Stock A and "
            f"<strong>${avg_b}</strong> toward Stock B with "
            f"<strong>{avg_conf}%</strong> average confidence and a "
            f"concentration index of <strong>{avg_aci}</strong> — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"are suitable for your portfolio this round."
        )

DATA_FILE = "/data/responses_A.csv"
CSV_HEADERS = (
    ["participant_id","condition","sector","hold_duration",
     "investment_goal","risk_tolerance","prolific_id",
     "started_at","completed_at"] +
    [f"R{r}_{f}" for r in range(1,16)
     for f in ["stock_a","stock_b","alloc","conf","aci","return"]] +
    ["total_return","benchmark_return","portfolio_score",
     "mean_confidence","mean_accuracy","oci","mean_aci","correct_rounds"] +
    ["age","gender","education","experience",
     "robo_prior","manipulation_check","open_text"]
)

def ensure_csv():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE,'w',newline='') as f:
            csv.DictWriter(f,fieldnames=CSV_HEADERS).writeheader()

def save_response(data):
    ensure_csv()
    with open(DATA_FILE,'a',newline='',encoding='utf-8') as f:
        csv.DictWriter(f,fieldnames=CSV_HEADERS,
                       extrasaction='ignore').writerow(data)

def calc_feedback(rd, start_r, end_r):
    allocs,confs,acis=[],[],[]
    rounds_detail=[]
    chart_data=[]
    for r in range(start_r, end_r+1):
        alloc=float(rd.get(f'R{r}_alloc',50))
        conf=float(rd.get(f'R{r}_conf',50))
        aci=abs(alloc-50)*2/100
        alloc_a=round(alloc*10); alloc_b=1000-alloc_a
        allocs.append(alloc); confs.append(conf); acis.append(aci)
        rounds_detail.append({"round":r,"alloc_a":alloc_a,
            "alloc_b":alloc_b,"conf":round(conf,1),"aci":round(aci,2)})
        chart_data.append({"round":r,"alloc_a":alloc_a,
            "alloc_b":alloc_b,"conf":round(conf,1),"aci":round(aci,2)})
    avg_slider=sum(allocs)/len(allocs) if allocs else 50
    return {
        "avg_a":round(avg_slider*10),
        "avg_b":1000-round(avg_slider*10),
        "avg_conf":round(sum(confs)/len(confs),1) if confs else 50.0,
        "avg_aci":round(sum(acis)/len(acis),2) if acis else 0.0,
        "rounds":rounds_detail,
        "chart_data":chart_data,
    }

def calc_final(sector, rd):
    rounds=ALL_ROUNDS.get(sector,ALL_ROUNDS["Information Technology"])
    total_return=benchmark_return=correct=0
    allocs,confs,acis=[],[],[]
    for row in rounds:
        rnd=row[0]
        alloc=float(rd.get(f'R{rnd}_alloc',50))
        conf=float(rd.get(f'R{rnd}_conf',50))
        growth_a=row[3]; growth_b=row[6]
        ra=growth_a/100; rb=growth_b/100
        aa=alloc*10; ab=1000-aa
        actual=(aa*ra)+(ab*rb); bench=(500*ra)+(500*rb)
        total_return+=actual; benchmark_return+=bench
        aci=abs(alloc-50)*2/100
        allocs.append(alloc); confs.append(conf); acis.append(aci)
        if actual>=bench: correct+=1
    mc=sum(confs)/len(confs) if confs else 50
    ma=(correct/15)*100
    return {
        "total_return":round(total_return,2),
        "benchmark_return":round(benchmark_return,2),
        "portfolio_score":round(total_return-benchmark_return,2),
        "mean_confidence":round(mc,1),
        "mean_accuracy":round(ma,1),
        "oci":round(mc-ma,1),
        "mean_aci":round(sum(acis)/len(acis),3) if acis else 0,
        "correct_rounds":correct,
    }

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    session.clear()
    session['participant_id']=str(uuid.uuid4())[:8]
    session['prolific_id']=request.args.get('PROLIFIC_PID','')
    session['condition']='A'
    session['started_at']=datetime.now().isoformat()
    session['rd']={}
    return render_template('welcome.html')

@app.route('/sector')
def sector_page():
    return render_template('sector.html')

@app.route('/sector', methods=['POST'])
def sector_submit():
    session['sector']=request.form.get('sector_choice','Information Technology')
    return redirect(url_for('prestudy'))

@app.route('/prestudy')
def prestudy():
    return render_template('prestudy.html')

@app.route('/prestudy', methods=['POST'])
def prestudy_submit():
    session['hold_duration']=request.form.get('hold_duration','')
    session['investment_goal']=request.form.get('investment_goal','')
    session['risk_tolerance']=request.form.get('risk_tolerance','')
    return redirect(url_for('round_page',rnd=1))

@app.route('/round/<int:rnd>')
def round_page(rnd):
    if rnd<1 or rnd>15: return redirect(url_for('final_results'))
    sector=session.get('sector','Information Technology')
    row=ALL_ROUNDS.get(sector,ALL_ROUNDS["Information Technology"])[rnd-1]
    rnd_num,sa,pa,ga,va,sb,pb,gb,vb=row
    change_a,end_a=get_final_change(pa,ga)
    change_b,end_b=get_final_change(pb,gb)
    rd=session.get('rd',{})
    ai_text=build_ai_text(rnd,sa,sb,
        session.get('investment_goal',''),
        session.get('risk_tolerance',''),
        session.get('hold_duration',''),rd)
    phase=get_phase(rnd)
    traj_a=generate_trajectory(pa,ga,va,seed=rnd*100+1)
    traj_b=generate_trajectory(pb,gb,vb,seed=rnd*100+2)
    return render_template('round.html',
        rnd=rnd,sa=sa,sb=sb,
        pa=pa,pb=pb,
        change_a=change_a,change_b=change_b,
        traj_a=json.dumps(traj_a),
        traj_b=json.dumps(traj_b),
        ai_text=ai_text,phase=phase,
        total_rounds=15,sector=sector)

@app.route('/round/<int:rnd>/submit',methods=['POST'])
def round_submit(rnd):
    sector=session.get('sector','Information Technology')
    alloc_a=float(request.form.get('alloc_a',500))
    alloc_pct=alloc_a/10
    conf=float(request.form.get('confidence',50))
    aci=abs(alloc_pct-50)*2/100
    row=ALL_ROUNDS.get(sector,ALL_ROUNDS["Information Technology"])[rnd-1]
    ga=row[3]; gb=row[6]
    ra=ga/100; rb=gb/100
    alloc_b=1000-alloc_a
    actual=(alloc_a*ra)+(alloc_b*rb)
    rd=session.get('rd',{})
    rd[f'R{rnd}_stock_a']=row[1]
    rd[f'R{rnd}_stock_b']=row[5]
    rd[f'R{rnd}_alloc']=alloc_pct
    rd[f'R{rnd}_conf']=conf
    rd[f'R{rnd}_aci']=round(aci,3)
    rd[f'R{rnd}_return']=round(actual,2)
    session['rd']=rd
    return redirect(url_for('trajectory',rnd=rnd))

@app.route('/trajectory/<int:rnd>')
def trajectory(rnd):
    sector=session.get('sector','Information Technology')
    row=ALL_ROUNDS.get(sector,ALL_ROUNDS["Information Technology"])[rnd-1]
    rnd_num,sa,pa,ga,va,sb,pb,gb,vb=row
    change_a,_=get_final_change(pa,ga)
    change_b,_=get_final_change(pb,gb)
    traj_a=generate_trajectory(pa,ga,va,seed=rnd*100+1)
    traj_b=generate_trajectory(pb,gb,vb,seed=rnd*100+2)
    if rnd==5: next_url=url_for('feedback',phase=1)
    elif rnd==10: next_url=url_for('feedback',phase=2)
    elif rnd==15: next_url=url_for('final_results')
    else: next_url=url_for('round_page',rnd=rnd+1)
    return render_template('trajectory.html',
        rnd=rnd,sa=sa,sb=sb,
        pa=pa,pb=pb,
        change_a=change_a,change_b=change_b,
        traj_a=json.dumps(traj_a),
        traj_b=json.dumps(traj_b),
        next_url=next_url,sector=sector)

@app.route('/feedback/<int:phase>')
def feedback(phase):
    sector=session.get('sector','Information Technology')
    rd=session.get('rd',{})
    start_r=1 if phase==1 else 6
    end_r=5 if phase==1 else 10
    summary=calc_feedback(rd,start_r,end_r)
    return render_template('feedback.html',
        phase=phase,summary=summary,
        start_r=start_r,end_r=end_r,
        next_round=6 if phase==1 else 11,
        sector=sector,
        goal=session.get('investment_goal',''),
        risk=session.get('risk_tolerance',''),
        hold=session.get('hold_duration',''))

@app.route('/final_results')
def final_results():
    sector=session.get('sector','Information Technology')
    rd=session.get('rd',{})
    results=calc_final(sector,rd)
    session['final_results']=results
    return render_template('final_results.html',results=results)

@app.route('/post_survey',methods=['GET','POST'])
def post_survey():
    if request.method=='POST':
        sector=session.get('sector','Information Technology')
        rd=session.get('rd',{})
        results=session.get('final_results',calc_final(sector,rd))
        row={
            'participant_id':session.get('participant_id'),
            'condition':'A','sector':sector,
            'hold_duration':session.get('hold_duration'),
            'investment_goal':session.get('investment_goal'),
            'risk_tolerance':session.get('risk_tolerance'),
            'prolific_id':session.get('prolific_id'),
            'started_at':session.get('started_at'),
            'completed_at':datetime.now().isoformat(),
            **{k:v for k,v in rd.items()},**results,
            'age':request.form.get('age'),
            'gender':request.form.get('gender'),
            'education':request.form.get('education'),
            'experience':request.form.get('experience'),
            'robo_prior':request.form.get('robo_prior'),
            'manipulation_check':request.form.get('manipulation_check'),
            'open_text':request.form.get('open_text'),
        }
        save_response(row)
        return redirect(url_for('thankyou',pid=session.get('prolific_id','')))
    return render_template('post_survey.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html',pid=request.args.get('pid',''))

@app.route('/admin')
def admin():
    pw=request.args.get('pw','')
    if pw!='raj_admin_2024':
        return render_template('admin_login.html')
    responses=[]; total=0; avg_oci=0; cond_a=0; cond_b=0
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,'r',encoding='utf-8') as f:
            reader=csv.DictReader(f)
            rows=list(reader)
            total=len(rows)
            responses=rows[-20:][::-1]
            ocis=[]
            for r in rows:
                try: ocis.append(float(r.get('oci',0)))
                except: pass
                if r.get('condition')=='A': cond_a+=1
                else: cond_b+=1
            if ocis: avg_oci=round(sum(ocis)/len(ocis),1)
    return render_template('admin.html',
        total=total,responses=responses,
        avg_oci=avg_oci,cond_a=cond_a,cond_b=cond_b)

@app.route('/data')
def download_data():
    pw=request.args.get('pw','')
    if pw!='raj_data_conditionA_2024': return "Access denied",403
    if not os.path.exists(DATA_FILE): return "No data yet",404
    with open(DATA_FILE,'r',encoding='utf-8') as f:
        content=f.read()
    return content,200,{'Content-Type':'text/csv',
        'Content-Disposition':'attachment; filename=responses_A.csv'}

@app.route('/ping')
def ping():
    return 'alive',200

if __name__=='__main__':
    ensure_csv()
    app.run(debug=True,port=5000)
