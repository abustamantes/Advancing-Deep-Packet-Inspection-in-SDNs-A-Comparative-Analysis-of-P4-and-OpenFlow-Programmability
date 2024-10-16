# Advancing-Deep-Packet-Inspection-in-SDNs-A-Comparative-Analysis-of-P4-and-OpenFlow-Programmability

## Research Project Overview

This thesis explores the efficacy of implementing Deep Packet Inspection (DPI) in Software-Defined Networks (SDNs), comparing two approaches: Data Plane-based DPI and Control Plane-based DPI. The study focuses on evaluating the latency, accuracy, resource utilization, and scalability of these implementations to determine which approach offers the most effective solution for real-time network threat detection and mitigation.

### Directory Structure

- `/thesis/`
  - `/HTTP_TEST/` - Contains flowcache files for HTTP-based Deep Packet Inspection testing.
    - `/data_plane/` - DPI implementation on the Data Plane.
    - `/control_plane/` - DPI implementation on the Control Plane.
  - `/POX_Applications/` - Contains POX controller applications.
  - `/SQL_TEST/` - Contains flowcache files for SQL-based Deep Packet Inspection testing.
  - `/pox/` - Contains POX controller scripts.
  - `/Manual_to_use_testing_framework.pdf` - Manual with guidelines on how to use the testing framework.
  - `/Tests and Results.pdf` - Tests and results for the research project. It describes in detail the type of tests, and interpretation of the results.
  - `/OVF P4 vs Openflow.ovf` - OVF file for setting up the virtualized environment.
  - `/OVF P4 vs Openflow.zip` - Compressed file containing the OVF setup.
  - `/README.md` - Overview and setup instructions for the project.
  - `/database_schema.sql` - SQL schema files for database setup.

## Research Objectives
  ### Evaluate DPI Performance: 
  Assess and compare the performance of DPI implementations using OpenFlow and P4 in terms of latency, accuracy, and resource utilization.
  ### Programmability and Flexibility: 
  Analyze how P4 enhances DPI functionalities beyond the limitations of OpenFlow, particularly at the application layer.
  ### Real-World Application: 
  Simulate real-world network scenarios to test the efficacy of DPI strategies in detecting and managing network threats, particularly focusing on HTTP and SQL traffic.

## Methodology
  ### Experimental Setup: 
  Utilization of Open vSwitch and BMv2 switches to create test environments that mimic real-world network conditions.
  ### Performance Metrics: 
  Measurement of key performance indicators such as packet processing speed, system resource usage, and the accuracy of threat detection.
  ### Statistical Analysis: 
  Use of advanced statistical tools to analyze the collected data, providing a robust framework for interpreting the results.

## Implementation Details

  ### OpenFlow-based DPI: 
  Implemented using POX controller to manage Open vSwitch, focusing on data inspection on L7 protocols.
  ### P4runtime-based DPI: 
  Utilized the P4 language to program BMv2 switches, enabling deeper packet inspection at the application layer.
  ### Data Plane-Centric DPI Strategy: 
  Developed a novel approach by embedding DPI functionalities directly into the data plane using P4, thereby reducing dependency on the control plane.

## Key Findings:

  ### Performance: 
  P4 implementations generally outperformed OpenFlow in terms of processing speed and flexibility.
  ### Resource Utilization: 
  Data Plane-Centric DPI with P4 showed lower latency and resource usage, proving its effectiveness in high-speed network environments.
  ### Accuracy: 
  Data Plane-Centric DPI with P4 had the better threat accuracy detection than OpenFlow-based DPI and P4runtime-based DPI for our URL filtering and SQL command filtering applications.

## Contact
For any queries related to this research, please contact Anthony J. Bustamante at email: bustamantesuareza3@gmail.com.
