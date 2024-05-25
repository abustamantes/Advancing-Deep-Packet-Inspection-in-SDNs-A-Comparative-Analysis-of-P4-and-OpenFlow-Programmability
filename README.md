# Advancing-Deep-Packet-Inspection-in-SDNs-A-Comparative-Analysis-of-P4-and-OpenFlow-Programmability

## Research Project Overview

This thesis explores the efficacy of implementing Deep Packet Inspection (DPI) in Software-Defined Networks (SDNs), comparing two approaches: Data Plane-based DPI and Control Plane-based DPI. The study focuses on evaluating the latency, accuracy, resource utilization, and scalability of these implementations to determine which approach offers the most effective solution for real-time network threat detection and mitigation.

### Directory Structure

- `/thesis/`
  - `/code/` - Contains all source code for DPI implementations.
    - `/data_plane/` - DPI implementation on the Data Plane.
    - `/control_plane/` - DPI implementation on the Control Plane.
  - `/utility_scripts/` - Scripts for setup, configuration, and testing.
  - `/documentation/` - Detailed documentation and the complete thesis report.
  - `/thesis.pdf` - Compiled comprehensive thesis document.
  - `/figures/` - Charts and visualizations of the experimental results.
  - `/tests/` - Testing frameworks and results.
    - `/latency/` - Scripts for latency testing.
    - `/accuracy/` - Tools for assessing the accuracy of DPI implementations.
    - `/resource_usage/` - Scripts for measuring CPU and memory usage.
  - `README.md` - Overview and setup instructions for the project.

## Research Objectives
  ### Evaluate DPI Performance: 
  Assess and compare the performance of DPI implementations using OpenFlow and P4 in terms of latency, accuracy, and resource utilization.
  ### Programmability and Flexibility: 
  Analyze how P4 enhances DPI functionalities beyond the limitations of OpenFlow, particularly at the application layer.
  ### Real-World Application: 
  Simulate real-world network scenarios to test the efficacy of DPI strategies in detecting and managing network threats, particularly focusing on HTTP and SQL traffic.
