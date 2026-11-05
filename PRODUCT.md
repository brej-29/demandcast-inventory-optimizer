# DemandCast

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Delegated by the brief. Browser-local JavaScript for the public workbench; existing Python research code retained for reproducibility and baseline auditing.

## Users

Product hypothesis: independent retail operators who already export daily item sales and need to decide how many units to buy before a supplier delivery. No customer interviews or commercial validation have been performed.

## Product Purpose

Turn daily sales into a transparent replenishment decision, with historical checks of the requested coverage. The current code confuses variation in future forecasts with forecast error; the rebuild makes that distinction inspectable.

## Operating Context

One item at a time, daily complete sales history, fixed supplier lead time, periodic stock review. Users supply on-hand units, incoming units arriving within the protection period, backorders, review frequency, and pack size. Sales are a proxy for demand, not proof of unconstrained demand.

## Capabilities and Constraints

CSV import, local computation, forecast comparison, historical coverage, what-if inputs, and decision CSV export. No accounts, external inference services, automatic purchasing, or uploaded customer records. Synthetic examples must be labeled. Historical performance is not a service guarantee. Budget is zero; no new account or card without approval.

## Evidence on Hand

Legacy source and tests; synthetic demo artifacts; UCI Online Retail dataset (CC BY 4.0) selected for a public benchmark. No evidence of revenue or actual stockout reduction.

## Product Principles

Prefer a measured simple baseline; expose the cost of uncertainty; fail closed on bad input; explain each quantity; distinguish observed sales from latent demand.

## Accessibility & Inclusion

WCAG AA, keyboard operation, reduced motion, responsive phone to desktop, accessible chart summary and table.
