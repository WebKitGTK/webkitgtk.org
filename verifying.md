---
layout: default
---

# Verifying Releases

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


### Checking

The signature file for each release has the same name plus the `.asc` suffix.
Given a download URL, the following illustrates the process:

```
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.34.3.tar.xz
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.34.3.tar.xz.asc
```

Now it is possible to verify the `.tar.xz` file against its signature:

```
% gpg --verify webkitgtk-2.34.3.tar.xz.asc
gpg: assuming signed data in 'webkitgtk-2.34.3.tar.xz'
gpg: Signature made lun 20 dic 2021 12:41:15 EET
gpg:                using DSA key D7FCF61CF9A2DEAB31D81BD3F3D322D0EC4582C3
gpg: Good signature from "Carlos Garcia Campos <cgarcia@igalia.com>" [full]
Primary key fingerprint: D7FC F61C F9A2 DEAB 31D8  1BD3 F3D3 22D0 EC45 82C3
```

### Keys

The following PGP keys are currently in use for signing releases:

<table>
  <thead>
    <tr><th>Developer</th><th>Fingerprint</th></tr>
  </thead>
    <tr>
      <td>Adrián Pérez de Castro (<a href="aperez.key">key</a>)</td>
      <td><tt>5AA3 BC33 4FD7 E336 9E7C  77B2 91C5 59DB E4C9 123B</tt></td>
    </tr>
    <tr>
      <td>Carlos García Campos (<a href="carlosgc.key">key</a>)</td>
      <td><tt>D7FC F61C F9A2 DEAB 31D8  1BD3 F3D3 22D0 EC45 82C3</tt></td>
    </tr>
  <tbody>
  </tbody>
</table>


Once downloaded, keys need to be imported in the PGP keyring, for example with
GnuPG:

```
% gpg --import carlosgc.key
gpg: key F3D322D0EC4582C3: 3 signatures not checked due to missing keys
gpg: key F3D322D0EC4582C3: public key "Carlos Garcia Campos <cgarcia@igalia.com>" imported
gpg: Total number processed: 1
gpg:               imported: 1
gpg: no ultimately trusted keys found
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
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.34.3.tar.xz
% curl -sLO https://webkitgtk.org/releases/webkitgtk-2.34.3.tar.xz.sums
% sha256sum webkitgtk-2.34.3.tar.xz | cut -f1 -d' '
0d2f37aa32e21a36e4dd5a5ce7ae5ce27435c29d6803b962b8c90cb0cc49c52d
```

This can be compared with the value of the last line of the `.sums` file:

```
% cat webkitgtk-2.34.3.tar.xz.sums
webkitgtk-2.34.3.tar.xz (23.8MB)
   md5sum: de30c41fb57b2b024417669c22914752
   sha1sum: 42b96ddaa89f7c3757860efd0b983f6e5b6ade51
   sha256sum: 0d2f37aa32e21a36e4dd5a5ce7ae5ce27435c29d6803b962b8c90cb0cc49c52d
```

Or, programmatically:

```
% expected=$(tail -1 webkitgtk-2.34.3.tar.xz.sums | cut -f5 -d' ')
% calculated=$(sha256sum webkitgtk-2.34.3.tar.xz | cut -f1 -d' ')
% if [ "$expected" = "$calculated" ]; then echo ok ; else echo failed ; fi
ok
```
