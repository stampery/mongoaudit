**************
Introduction
**************

It is widely known that there are quite a few holes in MongoDB's default configuration settings. This fact, combined with abundant lazy system administrators and developers, has led to what the press has called the MongoDB apocalypse.

**mongoaudit** not only detects misconfigurations, known vulnerabilities and bugs but also gives you advice on how to fix them, recommends best practices and teaches you how to DevOp like a pro!

***************
Supported tests
***************

- MongoDB listens on a port different to default one
- Server only accepts connections from whitelisted hosts / networks
- MongoDB HTTP status interface is not accessible on port 28017
- MongoDB is not exposing its version number
- MongoDB version is newer than 2.4
- TLS/SSL encryption is available
- TLS/SSL encryption is enabled
- TLS/SSL certificate is valid (not self-signed)
- Authentication is enabled
- SCRAM-SHA-1 authentication method is enabled
- Server-side Javascript is forbidden *
- Roles granted to the user only permit CRUD operations *
- The user has permissions over a single database *
- Security bug CVE-2015-7882
- Security bug CVE-2015-2705
- Security bug CVE-2014-8964
- Security bug CVE-2015-1609
- Security bug CVE-2014-3971
- Security bug CVE-2014-2917
- Security bug CVE-2013-4650
- Security bug CVE-2013-3969
- Security bug CVE-2012-6619
- Security bug CVE-2013-1892
- Security bug CVE-2013-2132

*Tests marked with an asterisk (\*) require valid authentication credentials.*

*********************************
How can I best secure my MongoDB?
*********************************

Once you run any of the test suites provided by mongoaudit, it will offer you to receive a fully detailed report via email. This personalized report links to a series of useful guides on how to fix every specific issue and how to harden your MongoDB deployments.

For your convenience, we have also published the mongoaudit guides in our `Medium publication <https://medium.com/mongoaudit>`_
.

************
Contributing
************

We're happy you want to contribute! You can help us in different ways:

- Open an issue in GitHub with suggestions for improvements and errors you're facing.
- Fork the repository and submit a pull request.
- Improve the documentation.

To submit a pull request, fork the mongoaudit repository and then clone your fork.

``git clone git@github.com:<your-name>/mongoaudit.git``

Make your suggested changes, git push and then submit a pull request.

*****
Legal
*****

License
=======

mongoaudit is released under the `MIT License <https://github.com/stampery/mongoaudit/blob/master/LICENSE>`_
.

Disclaimer
==========

``"With great power comes great responsibility"``

- Never use this tool on servers you don't own. Unauthorized access to strangers' computer systems is a crime in many countries.
- Please use this tool is at your own risk. We will accept no liability for any loss or damage which you may incur no matter how caused.
- Don't be evil!

Suport and trademarks
=====================

*This software is not supported or endorsed in any way by MongoDB Inc., Compose Inc., ObjectsLab Corporation nor other products or services providers it interoperates with. It neither tries to mimic or replace any software originally conceived by the owners of those products and services. In the same manner, any third party's trademark or intellectual property that may appear in this software must be understood as a strictly illustrative reference to the service provider it represents, and is never used in any way that may lead to confusion, so no abuse is intended.*

