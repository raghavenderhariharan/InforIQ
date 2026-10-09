# InforIQ platform dashboard

Source for the InforIQ platform Dashboard artifact, built from the whiteboard architecture
(Syteline / FT / CPQ → S3 data lake → Iceberg → canonical model → event hub → ERX with IQ rules → HITL → agents via ERP MCP)
and the Infor IQ component map.

- `index.html` — the dashboard page (runs inside the Dashboard artifact type, which supplies `dash` and `d3`).
- `data/*.json` — illustrative sample datasets; regenerate with `python3 generate_sample_data.py`.

Pages: Overview (KPIs, flow diagram, component health), Data pipeline, Events and decisions, Review queue.
All figures are sample data until the datasets are pointed at real sources.
