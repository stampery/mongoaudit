<div align="center">
    <h1><a href="https://mongoaud.it"><img src="https://raw.githubusercontent.com/stampery/mongoaudit/master/rsc/github-header.png" alt="mongoaudit"/></a></h1>
    <a href="https://travis-ci.org/stampery/mongoaudit"><img src="https://travis-ci.org/stampery/mongoaudit.svg?branch=master"></a>
    <a href="https://landscape.io/github/stampery/mongoaudit/master"><img alt="Code Health" src="https://landscape.io/github/stampery/mongoaudit/master/landscape.svg?style=flat"/></a>
    <a href="https://codeclimate.com/repos/588f61f717e4fe24b80046f6/feed"><img alt="Code Climate" src="https://codeclimate.com/repos/588f61f717e4fe24b80046f6/badges/ed691ca1655c0eb8a4a5/gpa.svg" /></a>
    <a href="https://codeclimate.com/repos/588f61f717e4fe24b80046f6/feed"><img alt="Issue Count" src="https://codeclimate.com/repos/588f61f717e4fe24b80046f6/badges/ed691ca1655c0eb8a4a5/issue_count.svg" /></a>
    <br/><br/>
    <p><strong>mongoaudit</strong> is a CLI tool for auditing MongoDB servers, detecting poor security settings and performing automated penetration testing.</p>
</div>

<h2 align="center">Installing</h2>

Clone this repository and run the setup:

```bash
> git clone https://github.com/stampery/mongoaudit.git
> cd mongoaudit
> python setup.py install
> mongoaudit
```

<h2 align="center">Introduction</h2>
<p>It is widely known that there are quite a few holes in MongoDB's default configuration settings. This fact, combined with abundant lazy system administrators and developers, has led to what the press has called the <a href="http://thenextweb.com/insider/2017/01/08/mongodb-ransomware-exists-people-bad-security/"><i>MongoDB apocalypse</i></a>.</p>

<p><strong>mongoaudit</strong> not only detects misconfigurations, known vulnerabilities and bugs but also gives you advice on how to fix them, recommends best practices and teaches you how to DevOp like a pro! </p>

<p>This is how the actual app looks like:</p>

<p align="center">
    <img align="center" src="https://raw.githubusercontent.com/stampery/mongoaudit/master/rsc/screenshot.png" alt="mongoaudit screenshot"/>
    <br /><i>Yep, that's material design on a console line interface. (Powered by <a href="https://github.com/urwid/urwid">urwid</a>)</i>
</p>

<h2 align="center">Supported tests</h2>

* MongoDB listens on a port different to default one
* Server only accepts connections from whitelisted hosts / networks
* MongoDB HTTP status interface is not accessible on port 28017
* MongoDB is not exposing its version number
* MongoDB version is newer than 2.4
* TLS/SSL encryption is enabled
* Authentication is enabled
* SCRAM-SHA-1 authentication method is enabled
* Server-side Javascript is forbidden *
* Roles granted to the user only permit CRUD operations *
* The user has permissions over a single database *
* Security bug [CVE-2015-7882](https://jira.mongodb.org/browse/SERVER-20691)
* Security bug [CVE-2015-2705](https://jira.mongodb.org/browse/SERVER-17521)
* Security bug [CVE-2014-8964](https://jira.mongodb.org/browse/SERVER-17252)
* Security bug [CVE-2015-1609](https://jira.mongodb.org/browse/SERVER-17264)
* Security bug [CVE-2014-3971](https://jira.mongodb.org/browse/SERVER-13753)
* Security bug [CVE-2014-2917](https://jira.mongodb.org/browse/SERVER-13644)
* Security bug [CVE-2013-4650](https://jira.mongodb.org/browse/SERVER-9983)
* Security bug [CVE-2013-3969](https://jira.mongodb.org/browse/SERVER-9878)
* Security bug [CVE-2012-6619](https://www.cvedetails.com/cve/CVE-2012-6619/)
* Security bug [CVE-2013-1892](https://www.cvedetails.com/cve/CVE-2013-1892/)
* Security bug [CVE-2013-2132](https://www.cvedetails.com/cve/CVE-2013-2132/)


_Tests marked with an asterisk (`*`) require valid authentication credentials._


<h2 align="center">How can I best secure my MongoDB?</h2>

Once you run any of the test suites provided by __mongoaudit__, it will offer you to receive a fully detailed report via email. This personalized report links to a series of useful guides on how to fix every specific issue and how to harden your MongoDB deployments.

For your convenience, we have also published the __mongoaudit__ guides in our [Medium publication](https://medium.com/mongoaudit).

<h2 align="center">Contributing</h2>

We're happy you want to contribute! You can help us in different ways:

* Open an issue with suggestions for improvements and errors you're facing.
* Fork this repository and submit a pull request.
* Improve the documentation.

To submit a pull request, fork the mongoaudit repository and then clone your fork:

```bash
git clone git@github.com:<your-name>/mongoaudit.git
```

Make your suggested changes, `git push` and then submit a pull request.

<h2 align="center">Legal</h2>

<h3>License</h3>
<strong>mongoaudit</strong> is released under the [MIT License](https://github.com/stampery/mongoaudit/blob/master/LICENSE).

<h3>Disclaimer</h3>

    "With great power comes great responsibility"

* Never use this tool on servers you don't own. Unauthorized access to strangers' computer systems is a crime in many countries.
* Please use this tool is at your own risk. We will accept no liability for any loss or damage which you may incur no matter how caused.
* Don't be evil! :trollface:

<h3>Suport and trademarks</h3>
<i>This software is not supported or endorsed in any way by MongoDB Inc., Compose Inc., ObjectsLab Corporation nor other products or services providers it interoperates with. It neither tries to mimic or replace any software originally conceived by the owners of those products and services. In the same manner, any third party's trademark or intellectual property that may appear in this software must be understood as a strictly illustrative reference to the service provider it represents, and is never used in any way that may lead to confusion, so no abuse is intended.</i>

[<img style="width:100%;" src="https://raw.githubusercontent.com/trailbot/vault/master/dist/img/footer.png">](https://stampery.com)
