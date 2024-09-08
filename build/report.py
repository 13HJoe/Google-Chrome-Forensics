import os
import sqlite3
import datetime

def write_to_html(data):
    for i in range(len(data)):
      temp = "<tr class='even dc 1'><td class='state'>"+str(data[i])+"</td></tr>"
      code += temp
    trail = """</table><br /><br /><br /></body></html>"""
    code+=trail
      
    with open("report.html", 'w') as obj:
        obj.write(code)

db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
connection = sqlite3.connect(db)
cursor = connection.cursor()
'''
cursor.execute("select sql from sqlite_schema where name = 'downloads';")
data = cursor.fetchall()
data = str(data)
data = data.split(",")
for line in data:
    print(line)
'''

cursor.execute("SELECT * FROM downloads;")
with open("report.html", 'w') as obj:
  code = """<!DOCTYPE html>
<!-- saved from url=(0016)http://localhost -->
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ms="urn:schemas-microsoft-com:xslt" xmlns:bat="http://schemas.microsoft.com/battery/2012" xmlns:js="http://microsoft.com/kernel">
  <head>
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="ReportUtcOffset" content="+5:30" />
    <title>Battery report</title>
    <style type="text/css">
      body {
        font-family: Segoe UI Light;
        letter-spacing: 0.02em;
        background-color: #181818;
        color: #F0F0F0;
        margin-left: 5.5em;
      }

      h1 {
        color: #11D8E8;
        font-size: 42pt;
      }

      h2 {
        font-size: 15pt;
        color: #11EEF4;
        margin-top: 4em;
        margin-bottom: 0em;
        letter-spacing: 0.08em;
      }

      td {
        padding-left: 0.3em;
        padding-right: 0.3em;
      }

      .nobatts {
        font-family: Segoe UI Semibold;
        background: #272727;
        color: #ACAC60;
        font-size: 13pt;
        padding-left: 0.4em;
        padding-right: 0.4em;
        padding-top: 0.3em;
        padding-bottom: 0.3em;
      }

      .explanation {
        color: #777777;
        font-size: 12pt;
        margin-bottom: 1em;
      }

      .explanation2 {
        color: #777777;
        font-size: 12pt;
        margin-bottom: 0.1em;
      }

      table {
        border-width: 0;
        table-layout: fixed;
        font-family: Segoe UI Light;
        letter-spacing: 0.02em;
        background-color: #181818;
        color: #f0f0f0;
      }

      .even {
        background: #272727;
      }

      .odd {
        background: #1E1E1E;
      }

      .even.suspend {
        background: #1A1A28;
      }

      .odd.suspend {
        background: #1A1A2C;
      }

      thead {
        font-family: Segoe UI Semibold;
        font-size: 85%;
        color: #BCBCBC;
      }

      text {
        font-size: 12pt;
        font-family: Segoe UI Light;
        fill: #11EEF4;
      }

      .centered {
        text-align: center;
      }

      .label {
        font-family: Segoe UI Semibold;
        font-size: 85%;
        color: #BCBCBC;
      }

      .dc.even {
        background: #40182C;
      }

      .dc.odd {
        background: #30141F;
      }

      td.colBreak {
        padding: 0;
        width: 0.15em;
      }

      td.state {
        text-align: center;
      }

      td.hms {
        font-family: Segoe UI Symbol;
        text-align: right;
        padding-right: 3.4em;
      }

      td.dateTime {
        font-family: Segoe UI Symbol;
      }

      td.nullValue {
        text-align: center;
      }

      td.percent {
        font-family: Segoe UI Symbol;
        text-align: right;
        padding-right: 2.5em;
      }

      col:first-child {
        width: 13em;
      }

      col.col2 {
        width: 10.4em;
      }

      col.percent {
        width: 7.5em;
      }

      td.mw {
        text-align: right;
        padding-right: 2.5em;
      }

      td.acdc {
        text-align: center;
      }

      span.date {
        display: inline-block;
        width: 5.5em;
      }

      span.time {
        text-align: right;
        width: 4.2em;
        display: inline-block;
      }

      text {
        font-family: Segoe UI Symbol;
      }

      .noncontigbreak {
        height: 0.3em;
        background-color: #1A1A28;
      }
    </style>
  </head>
  <body>
    <h1> Google Chrome Forensic Report </h1>
      <tr>
        <td class="label"> REPORT TIME </td>
        <td class="dateTime">
          <span class="date">f</span>
          <span class="time">f</span>
        </td>
      </tr>
    </table>
    <h2> Installed batteries </h2>
    <div class="explanation"> Information about each currently installed battery </div>
    <table>
      <colgroup>
        <col style="width: 15em;" />
        <col style="width: 14em;" />
      </colgroup>
      <thead>
        <tr>
          <td></td>
          <td> BATTERY 1</td>
        </tr>
      </thead>
      <tr>
        <td>
          <span class="label">NAME</span>
        </td>
        <td>Primary</td>
      </tr>
      <tr>
        <td>
          <span class="label">MANUFACTURER</span>
        </td>
        <td>HP</td>
      </tr>
      <tr>
        <td>
          <span class="label">SERIAL NUMBER</span>
        </td>
        <td>SerialNumber</td>
      </tr>
      <tr>
        <td>
          <span class="label">CHEMISTRY</span>
        </td>
        <td>LION</td>
      </tr>
      <tr>
        <td>
          <span class="label">DESIGN CAPACITY</span>
        </td>
        <td>28,693 mWh </td>
      </tr>
      <tr style="height:0.4em;"></tr>
      <tr>
        <td>
          <span class="label">FULL CHARGE CAPACITY</span>
        </td>
        <td>28,693 mWh </td>
      </tr>
      <tr>
        <td>
          <span class="label">CYCLE COUNT</span>
        </td>
        <td> - </td>
      </tr>
    </table>
    <h2>Bookmarks</h2>
    <div class="explanation"> Chrome Forensics - Download History </div>
    <table>
      <colgroup>
        <col />
        <col class="col2" />
        <col style="width: 4.2em;" />
        <col class="percent" />
        <col style="width: 11em;" />
      </colgroup>
      <thead>
        <tr>
          <td colspan="2" class="centered"> Download Data </td>
        </tr>
      </thead>
      """
  for line in cursor.fetchall():
      line = "<tr class='even dc 1'><td class='state'>" + str(line) + "</td></tr>"
      code +=  line
  code+="""</table><br /><br /><br /></body></html>"""
  obj.write(code)