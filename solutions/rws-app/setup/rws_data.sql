-- Infrastructure Management Data schema and data for RWS

-- Create Regions table
CREATE TABLE Regions (
    RegionID INT PRIMARY KEY,
    RegionName NVARCHAR(50) NOT NULL,
    RegionalDirector NVARCHAR(100) NULL,
    MainOfficeLocation NVARCHAR(100) NULL
);

-- Create InfrastructureAssets table
CREATE TABLE InfrastructureAssets (
    AssetID INT PRIMARY KEY,
    AssetName NVARCHAR(100) NOT NULL,
    AssetType NVARCHAR(50) NOT NULL, -- Bridge, Highway, Waterway, etc.
    ConstructionYear INT NULL,
    LastMajorMaintenance DATE NULL,
    Status NVARCHAR(50) NOT NULL, -- Operational, Under Maintenance, Critical, etc.
    RegionID INT NOT NULL,
    FOREIGN KEY (RegionID) REFERENCES Regions(RegionID)
);

-- Create MaintenanceProjects table
CREATE TABLE MaintenanceProjects (
    ProjectID INT PRIMARY KEY,
    AssetID INT NOT NULL,
    ProjectName NVARCHAR(100) NOT NULL,
    ProjectType NVARCHAR(50) NOT NULL, -- Renovation, Inspection, Emergency Repair, etc.
    StartDate DATE NULL,
    EndDate DATE NULL,
    Budget DECIMAL(15, 2) NULL,
    Status NVARCHAR(50) NOT NULL, -- Planned, In Progress, Completed, etc.
    Priority NVARCHAR(20) NOT NULL, -- High, Medium, Low
    FOREIGN KEY (AssetID) REFERENCES InfrastructureAssets(AssetID)
);

-- Create SafetyInspections table
CREATE TABLE SafetyInspections (
    InspectionID INT PRIMARY KEY,
    AssetID INT NOT NULL,
    InspectionDate DATE NOT NULL,
    InspectorName NVARCHAR(100) NOT NULL,
    InspectionType NVARCHAR(50) NOT NULL, -- Routine, Emergency, Follow-up
    SafetyRating INT NOT NULL, -- 1-5 scale
    Findings NVARCHAR(MAX) NULL,
    RecommendedActions NVARCHAR(MAX) NULL,
    FOREIGN KEY (AssetID) REFERENCES InfrastructureAssets(AssetID)
);
GO

-- Insert data into Regions
INSERT INTO Regions (RegionID, RegionName, RegionalDirector, MainOfficeLocation) VALUES
(1, 'Noord-Nederland', 'Jan de Vries', 'Groningen'),
(2, 'Oost-Nederland', 'Emma Bakker', 'Zwolle'),
(3, 'Midden-Nederland', 'Lucas van Dijk', 'Utrecht'),
(4, 'West-Nederland Noord', 'Sophie Jansen', 'Haarlem'),
(5, 'West-Nederland Zuid', 'Thomas Visser', 'Rotterdam'),
(6, 'Zuid-Nederland', 'Maria van den Berg', 'Eindhoven'),
(7, 'Zee en Delta', 'Peter de Groot', 'Middelburg');

-- Insert data into InfrastructureAssets
INSERT INTO InfrastructureAssets (AssetID, AssetName, AssetType, ConstructionYear, LastMajorMaintenance, Status, RegionID) VALUES
(101, 'Van Brienenoordbrug', 'Bridge', 1965, '2020-06-15', 'Operational', 5),
(102, 'Afsluitdijk', 'Dam', 1932, '2023-12-10', 'Under Maintenance', 1),
(103, 'A12 Utrecht-Duitse grens', 'Highway', 1962, '2022-08-20', 'Operational', 3),
(104, 'Noordzeekanaal', 'Waterway', 1876, '2021-05-30', 'Operational', 4),
(105, 'Haringvlietdam', 'Dam', 1971, '2019-11-15', 'Operational', 7),
(106, 'Zeelandbrug', 'Bridge', 1965, '2023-03-25', 'Operational', 7),
(107, 'A2 Tunnel Maastricht', 'Tunnel', 2016, '2022-09-08', 'Operational', 6),
(108, 'IJssel-Twentekanaal', 'Waterway', 1936, '2023-07-12', 'Under Maintenance', 2),
(109, 'Prins Clausplein', 'Junction', 1982, '2024-01-20', 'Operational', 5),
(110, 'Ketelbrug', 'Bridge', 1970, '2021-12-05', 'Critical', 2);

-- Insert data into MaintenanceProjects (Last 12 months)
INSERT INTO MaintenanceProjects (ProjectID, AssetID, ProjectName, ProjectType, StartDate, EndDate, Budget, Status, Priority) VALUES
(1001, 102, 'Afsluitdijk Renovation', 'Renovation', '2023-06-15', '2024-12-31', 1500000.00, 'In Progress', 'High'),
(1002, 108, 'IJssel Waterway Dredging', 'Maintenance', '2023-07-01', '2024-08-30', 750000.00, 'In Progress', 'Medium'),
(1003, 110, 'Ketelbrug Emergency Repair', 'Emergency Repair', '2024-02-15', '2024-06-30', 900000.00, 'In Progress', 'High'),
(1004, 101, 'Bridge Support Inspection', 'Inspection', '2024-03-10', '2024-03-15', 50000.00, 'Completed', 'Medium'),
(1005, 105, 'Dam Safety Enhancement', 'Upgrade', '2024-01-20', '2024-07-31', 1200000.00, 'In Progress', 'High'),
(1006, 103, 'Highway Resurfacing A12', 'Maintenance', '2024-04-01', '2024-05-31', 300000.00, 'In Progress', 'Medium'),
(1007, 106, 'Bridge Joint Replacement', 'Repair', '2024-03-15', '2024-04-15', 150000.00, 'In Progress', 'Medium'),
(1008, 104, 'Canal Lock Maintenance', 'Maintenance', '2024-05-01', '2024-06-30', 400000.00, 'Planned', 'Low'),
(1009, 107, 'Tunnel Ventilation Upgrade', 'Upgrade', '2024-06-15', '2024-08-15', 600000.00, 'Planned', 'Medium'),
(1010, 109, 'Junction Lighting Renewal', 'Upgrade', '2024-04-20', '2024-05-20', 200000.00, 'In Progress', 'Low');

-- Insert data into SafetyInspections (Recent inspections)
INSERT INTO SafetyInspections (InspectionID, AssetID, InspectionDate, InspectorName, InspectionType, SafetyRating, Findings, RecommendedActions) VALUES
(5001, 110, '2024-02-10', 'Willem Smit', 'Emergency', 2, 'Structural integrity concerns in support beams', 'Immediate repair required; implement load restrictions'),
(5002, 102, '2024-03-01', 'Anna Hoekstra', 'Routine', 4, 'Minor wear on new protective coating', 'Schedule follow-up inspection in 6 months'),
(5003, 105, '2024-03-15', 'Dirk Vermeulen', 'Routine', 5, 'All systems functioning normally', 'Continue regular maintenance schedule'),
(5004, 101, '2024-03-10', 'Eva Mulder', 'Routine', 4, 'Minor corrosion on secondary supports', 'Plan preventive maintenance within 3 months'),
(5005, 108, '2024-02-25', 'Pieter de Jong', 'Follow-up', 3, 'Dredging required in northern section', 'Accelerate planned maintenance schedule'),
(5006, 103, '2024-04-01', 'Sarah van Leeuwen', 'Routine', 4, 'Surface wear within acceptable limits', 'Continue with planned resurfacing'),
(5007, 106, '2024-03-20', 'Mark Bakker', 'Follow-up', 4, 'Joint replacement proceeding as planned', 'No additional actions required'),
(5008, 104, '2024-04-05', 'Lisa de Wit', 'Routine', 5, 'Lock mechanisms operating efficiently', 'Schedule regular maintenance'),
(5009, 107, '2024-03-30', 'Rob Hendricks', 'Routine', 4, 'Ventilation systems meeting safety standards', 'Proceed with planned upgrade'),
(5010, 109, '2024-04-10', 'Karen van Dam', 'Routine', 4, 'Lighting systems functional but aging', 'Continue with renewal project');
GO

-- Create views for easy access to infrastructure data
CREATE VIEW vw_CriticalAssets AS
SELECT 
    a.AssetID,
    a.AssetName,
    a.AssetType,
    a.Status,
    r.RegionName,
    i.SafetyRating,
    i.InspectionDate
FROM 
    InfrastructureAssets a
    JOIN Regions r ON a.RegionID = r.RegionID
    LEFT JOIN SafetyInspections i ON a.AssetID = i.AssetID
WHERE 
    a.Status = 'Critical'
    OR (i.SafetyRating <= 2 AND i.InspectionDate = (
        SELECT MAX(InspectionDate)
        FROM SafetyInspections
        WHERE AssetID = a.AssetID
    ));
GO

CREATE VIEW vw_ActiveProjects AS
SELECT 
    p.ProjectID,
    p.ProjectName,
    p.ProjectType,
    p.StartDate,
    p.EndDate,
    p.Budget,
    p.Status,
    p.Priority,
    a.AssetName,
    a.AssetType,
    r.RegionName
FROM 
    MaintenanceProjects p
    JOIN InfrastructureAssets a ON p.AssetID = a.AssetID
    JOIN Regions r ON a.RegionID = r.RegionID
WHERE 
    p.Status IN ('Planned', 'In Progress');
GO
