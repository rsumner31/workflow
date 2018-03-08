# Chart Provenance

As of Workflow [v2.8.0](../changelogs/v2.8.0.md), Deis has released [Kubernetes Helm][helm] charts for Workflow
and for each of its [components](../understanding-workflow/components.md).

Helm provides tools for establishing and verifying chart integrity.  (For an overview, see the [Provenance](https://github.com/kubernetes/helm/blob/master/docs/provenance.md) doc.)  All release charts from the Deis Workflow team are now signed using this mechanism.

The full `Deis, Inc. (Helm chart signing key) <security@deis.com>` public key can be found [here](../security/1d6a97d0.txt), as well as the [pgp.mit.edu](http://pgp.mit.edu/pks/lookup?op=vindex&fingerprint=on&search=0x17E526B51D6A97D0) keyserver and the official Deis Keybase [account][deis-keybase].  The key's fingerprint can be cross-checked against all of these sources.

## Verifying a signed chart

The public key mentioned above must exist in a local keyring before a signed chart can be verified.

To add it to the default `~/.gnupg/pubring.gpg` keyring, any of the following commands will work:

```
$ # via our hosted location
$ curl https://deis.com/workflow/docs/security/1d6a97d0.txt | gpg --import

$ # via the pgp.mit.edu keyserver
$ gpg --keyserver pgp.mit.edu --recv-keys 1D6A97D0

$ # via Keybase with account...
$ keybase follow deis
$ keybase pgp pull

$ # via Keybase by curl
$ curl https://keybase.io/deis/key.asc | gpg --import
```

Charts signed with this key can then be verified when fetched:

```
$ helm repo add deis https://charts.deis.com/workflow
"deis" has been added to your repositories

$ helm fetch --verify deis/workflow --version v2.18.0
Verification: &{0xc42077e460 sha256:c8fe609e70f6f11299c2e1fa130433254d747fc0a694a2928a1c5d3d3c986ce8 workflow-v2.18.0.tgz}
```

One can then inspect the fetched `workflow-v2.18.0.tgz.prov` provenance file.

If the chart was not signed, the command above would result in:

```
Error: Failed to fetch provenance "https://charts.deis.com/workflow/workflow-v2.18.0.tgz.prov"
```

Alternatively, the chart can also be verified at install time:

```
$ helm install --verify deis/workflow --namespace deis
NAME:   exiled-mink
LAST DEPLOYED: Wed Sep  7 08:22:16 2017
NAMESPACE: deis
STATUS: DEPLOYED
...

$ helm ls
NAME       	REVISION	UPDATED                 	STATUS  	CHART
exiled-mink	1       	Wed Sep  7 08:22:16 2017	DEPLOYED	workflow-v2.18.0
```

Having done so, one is assured of the origin and authenticity of any installed Workflow chart released by Deis.

[helm]: https://github.com/kubernetes/helm/blob/master/docs/install.md
[deis-keybase]: https://keybase.io/deis
