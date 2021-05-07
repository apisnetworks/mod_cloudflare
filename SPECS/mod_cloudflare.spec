# apxs script location
%{!?_httpd_apxs: %global _httpd_apxs %{_bindir}/apxs}

# Module Magic Number
%{!?_httpd_mmn: %global _httpd_mmn %(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo missing-httpd-devel)}

# Configuration directory
%{!?_httpd_confdir: %global _httpd_confdir %{_sysconfdir}/httpd/conf.d}
%{!?_httpd_moddir: %global _httpd_moddir %{_libdir}/httpd/modules}

%define _gitdir %{_sourcedir}/mod_cloudflare

%global httpd24 1
%global rundir /run

Name:		mod_cloudflare
Version:	2021.5.3
Release:	1%{?dist}
Summary:	Apache module to show true visitor IPs in logs for domains using CloudFlare.
Group:		System Environment/Daemons
License:	ASL 2.0
URL:		https://github.com/apisnetworks/mod_cloudflare
Source0:  cloudflare.conf
Patch0: PR0030-Add-CLOUDFLARE_CONNECTION.patch
Patch1: PR0035-Update-IP-Addresses.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(id -nu)
BuildRequires:	httpd-devel >= 2.4, pkgconfig, fail2ban
Requires:	httpd-mmn = %{_httpd_mmn}

%description
Apache module to show true visitor IPs in logs for domains using CloudFlare.
CloudFlare acts as a proxy, which means that your visitors are routed through
the CloudFlare network and you do not see their original IP address. This
module uses HTTP headers provided by the CloudFlare proxy to log the real IP
address of the visitor.
Based on mod_remoteip.c, this Apache extension will replace the remote_ip
variable in user's logs with the correct remote_ip sent from CloudFlare. This
also does authentication, only performing the switch for requests the switch
for requests originating from CloudFlare IPs.

%prep
rm -rf %{_builddir}
mkdir %{_builddir}
cd %{_builddir}
cp -p %{_gitdir}/{README.md,LICENSE,ChangeLog,mod_cloudflare.c} %{_builddir}/
cp -p %{SOURCE0} cloudflare.conf
%patch0 -p1
%patch1 -p1

%build
%{_httpd_apxs} -c -Wc,"%{optflags} -Wall -pedantic -std=c99" mod_cloudflare.c

%install
rm -rf $RPM_BUILD_ROOT
install -Dm 755 .libs/mod_cloudflare.so $RPM_BUILD_ROOT%{_httpd_moddir}/mod_cloudflare.so
install -Dp -m 0644 cloudflare.conf $RPM_BUILD_ROOT%{_httpd_confdir}/cloudflare.conf

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.md LICENSE ChangeLog
%config(noreplace) %{_httpd_confdir}/cloudflare.conf
%{_httpd_moddir}/*.so

%changelog
* Fri May 07 2021 Matt Saladna <matt@apisnetworks.com> - 2021.5.7-1
- Merge CLOUDFLARE_CONNECTION patch, IP4 updates
- Initial forked release
