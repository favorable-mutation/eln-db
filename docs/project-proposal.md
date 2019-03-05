---
layout: default
title: Project Proposal
permalink: /project-proposal/
---
*by Griffin J Rademacher*

*Blackboard Group Name: Rademacher*

### Description

This project aims to provide a backend database system for use in an 
[ELN](https://en.wikipedia.org/wiki/Electronic_lab_notebook)
(electronic lab notebook) application. ELN systems are utilized by
modern scientific labs for tracking complex data gathered by researchers
conducting experiments in diverse areas. The optimal ELN setup allows storage of
empirical (that is to say, real and messy) data of a variety of types and
encourages standardization of data storage practices across a research group or
organization. It also allows multiple users to access data simultaneously, and
enables easy backup/duplication of data as well as easy sharing of data across
institutions (e.g. when sending findings to be published, and attempting to make
the research process transparent enough to convince skeptical reviewers that
results are not manufactured). This project will implement such features, and
specifically will expose necessary methods for experimental data storage,
dynamic creation of fields for that data within the default schema, data viewing
brokered by multiple accounts, and data modification or deletion. It will
provide a way for users to export data to various data analysis tools.

### Storage Solutions

Although scientific data can be messy, it is imperative for researchers to
develop a lab-wide standard for data collection and storage, for the practical
purpose of getting anything done. While a NoSQL storage solution might be useful
in a situation where one is modelling real world data, a SQL system is more
applicable to the situation of a typical (successful) lab, where data is
rigorously policed and delicately curated by researchers themselves in
anticipation of placing it on the proverbial desk of the aforementioned
reviewer. Data collected in an experimental context should have at least some
natural relationships inherent to it, which is better supported by SQL.

### Technology

This project will be implemented using `MySQL` to provide a database management
system, which will be interfaced with `R` via the [RMySQL
package](https://cran.r-project.org/web/packages/RMySQL/index.html) to provide
access to data for analysis. The interface to the database for input and
management of data will be provided through a webapp created with `Python` using the
[Flask framework](http://flask.pocoo.org/). This framework will also provide the
interface to the DBMS. 

### Motivation

![](https://i.kym-cdn.com/entries/icons/original/000/025/351/afoeeee.jpg)

As a combined Biology/CS major, I've spent time working in a lab setting, and am
interested in applying my skills to writing tools for enabling scientists to do
what they love. This project is an interesting experiment that I hope will
familiarize me with the challenges of creating useable software for the
scientific problem domain.
