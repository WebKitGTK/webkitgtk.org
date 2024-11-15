---
layout: post
title: Verifying Releases
---

WebKitGTK release tarballs are cryptographically signed and can be verified
using [PGP signatures](#pgp-signatures) (in an `.asc` file) and their
[checksums](#checksums) (in a `.sums` file). Everybody is encouraged to verify
the integrity of downloaded files using them.

## PGP Signatures

Every release is accompanied by a cryptographic signature produced by the
person in charge of publishing the release. This signature allows anyone to
check whether the files have been tampered with after they have been signed.
Forging a signature is practically impossible without gaining access to the
private key used. If that were to happen, the compromised key would be revoked
and all files re-signed with new keys.

### Keys

The following PGP keys are currently in use for signing releases:

<table>
  <thead>
    <tr><th>Developer</th><th>Fingerprint</th></tr>
  </thead>
    <tr>
      <td>Adrián Pérez de Castro (<a href="../keys/aperez.key">key</a>)</td>
      <td><tt>5AA3 BC33 4FD7 E336 9E7C  77B2 91C5 59DB E4C9 123B</tt></td>
    </tr>
    <tr>
      <td>Carlos García Campos (<a href="../keys/carlosgc.key">key</a>)</td>
      <td><tt>013A 0127 AC9C 65B3 4FFA 6252 6C10 09B6 9397 5393</tt></td>
    </tr>
  <tbody>
  </tbody>
</table>

### Importing keys

Once downloaded, keys need to be imported in the PGP keyring, for example with
GnuPG:

```
% gpg --import carlosgc.key
gpg: key 6C1009B693975393: 3 signatures not checked due to missing keys
gpg: key 6C1009B693975393: public key "Carlos Garcia Campos <cgarcia@igalia.com>" imported
gpg: Total number processed: 1
gpg:               imported: 1
gpg: no ultimately trusted keys found
```

### Checking

The signature file for each release has the same name plus the `.asc` suffix.
Given a download URL, the following illustrates the process:

```
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.45.1.tar.xz
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.45.1.tar.xz.asc
```

Now it is possible to verify the `.tar.xz` file against its signature:

```
% gpg --verify webkitgtk-2.45.1.tar.xz.asc
gpg: assuming signed data in 'webkitgtk-2.45.1.tar.xz'
gpg: Signature made Fri May 10 10:18:07 2024 CEST
gpg:                using RSA key 013A0127AC9C65B34FFA62526C1009B693975393
gpg: Good signature from "Carlos Garcia Campos <cgarcia@igalia.com>" [full]
```

## Checksums

Checksums for release tarballs are also published along releases. While
suitable to check file integrity, using [PGP signatures](#pgp-signatures)
provide a stronger guarantee.

### Checking

The checksums file for each release has the same name plus the `.sums` suffix.
Given a download URL, the following illustrates how to calculate the SHA-256
checksum on your end:

```
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.45.1.tar.xz
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.45.1.tar.xz.sums
% sha256sum webkitgtk-2.45.1.tar.xz | cut -f1 -d' '
9813f5dfb81717c1a427f6947654edad0bdc1e21445902fdb9b9a5589d36c38d
```

This can be compared with the value of the last line of the `.sums` file:

```
% cat webkitgtk-2.45.1.tar.xz.sums
webkitgtk-2.45.1.tar.xz (38.8MB)
   md5sum: 6f72d0a91b040d146738931357d70995
   sha1sum: 89c5838996561df50c53dc1f2722a7bc68c4a325
   sha256sum: 9813f5dfb81717c1a427f6947654edad0bdc1e21445902fdb9b9a5589d36c38d
```

Or, programmatically:

```
% expected=$(tail -1 webkitgtk-2.45.1.tar.xz.sums | cut -f5 -d' ')
% calculated=$(sha256sum webkitgtk-2.45.1.tar.xz | cut -f1 -d' ')
% if [ "$expected" = "$calculated" ]; then echo ok ; else echo failed ; fi
ok
```
