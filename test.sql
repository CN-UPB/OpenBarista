--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: datacenters; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY datacenters (created_at, modified_at, meta, uuid, name, description, type, datacenter_masta_id) FROM stdin;
\.


--
-- Data for Name: flavors; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY flavors (created_at, modified_at, meta, uuid, name, description, disk, ram, vcpus) FROM stdin;
2016-03-03 17:21:06.630632	2016-03-03 17:21:06.630632	null	da4ed525-194d-40b3-ba25-d79503e5b996	loadbalancer-VM-flv	Virtual machine containing loadbalancer image	0	512	1
2016-03-03 17:26:28.071451	2016-03-03 17:26:28.071451	null	0881267a-987b-4642-8eef-831780cb98ed	loadbalancer-VM-flv	Virtual machine containing loadbalancer image	0	512	1
2016-03-03 17:29:08.699244	2016-03-03 17:29:08.699244	null	a51184f4-6e22-469d-9f9b-56b202e07e57	loadbalancer-VM-flv	Virtual machine containing loadbalancer image	0	512	1
2016-03-03 17:35:33.635565	2016-03-03 17:35:33.635565	null	78d7f0b8-f17a-4491-abeb-c94d5a114842	loadbalancer-VM-flv	Virtual machine containing loadbalancer image	0	512	1
2016-03-03 17:35:33.810814	2016-03-03 17:35:33.810814	null	f1ca0b7e-c025-4043-b845-66740dd5a0c8	firewall-VM-flv	Virtual machine containing firewall image	0	512	1
2016-03-03 17:35:33.98131	2016-03-03 17:35:33.98131	null	dc4b4dd7-d656-4813-8883-4740fff1dabf	webserver-VM-flv	Generic Virtual Machine for webserver	0	512	1
2016-03-03 17:36:42.37558	2016-03-03 17:36:42.37558	null	342e1e53-bc37-4015-9414-362b3803e9d3	loadbalancer-VM-flv	Virtual machine containing loadbalancer image	0	512	1
2016-03-03 17:36:42.583887	2016-03-03 17:36:42.583887	null	41b7ff33-ddd1-46e4-ba90-9754868beef2	firewall-VM-flv	Virtual machine containing firewall image	0	512	1
2016-03-03 17:36:42.802281	2016-03-03 17:36:42.802281	null	be1ecbcf-18ff-420e-8765-771531a797f2	webserver-VM-flv	Generic Virtual Machine for webserver	0	512	1
2016-03-03 17:45:31.886694	2016-03-03 17:45:31.886694	null	afe6260a-0f40-4a1a-b77e-e9d576117631	loadbalancer-VM-flv	Virtual machine containing loadbalancer image	0	512	1
2016-03-03 17:45:32.07316	2016-03-03 17:45:32.07316	null	4453c898-4f1f-4d12-a1b6-1e6e83e3a021	firewall-VM-flv	Virtual machine containing firewall image	0	512	1
2016-03-03 17:45:32.242793	2016-03-03 17:45:32.242793	null	666bc93e-6018-47d5-946f-c685cd5d4212	webserver-VM-flv	Generic Virtual Machine for webserver	0	512	1
\.


--
-- Data for Name: datacenter_flavors; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY datacenter_flavors (created_at, modified_at, meta, uuid, name, description, masta_flavor_id, flavor_id, datacenter_id) FROM stdin;
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY images (created_at, modified_at, meta, uuid, name, description, location, username, password) FROM stdin;
2016-03-03 17:21:06.800237	2016-03-03 17:21:06.800237	null	390b3b8b-c297-47ef-9d40-467cc614822b	loadbalancer-VM-img	Image of the VNFC loadbalancer-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2	debian	R3L8uo725h1
2016-03-03 17:26:28.106596	2016-03-03 17:26:28.106596	null	ce785bfc-97fd-4c0e-88dd-02ba08303834	loadbalancer-VM-img	Image of the VNFC loadbalancer-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2	debian	R3L8uo725h1
2016-03-03 17:29:08.731049	2016-03-03 17:29:08.731049	null	8a7d4c74-a577-47ee-bb01-4057db91a33e	loadbalancer-VM-img	Image of the VNFC loadbalancer-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2	debian	R3L8uo725h1
2016-03-03 17:35:33.667526	2016-03-03 17:35:33.667526	null	4b5e626d-b2c0-494d-8412-ff7b6c0072d8	loadbalancer-VM-img	Image of the VNFC loadbalancer-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2	debian	R3L8uo725h1
2016-03-03 17:35:33.825818	2016-03-03 17:35:33.825818	null	136def80-a484-4a2f-81e6-a0201acc428d	firewall-VM-img	Image of the VNFC firewall-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/firewall.qcow2	debian	P34T8Yui3o1Z
2016-03-03 17:35:34.046467	2016-03-03 17:35:34.046467	null	e43d828d-e338-408e-9de6-aaf8d6688c23	webserver-VM-img	Image of the VNFC webserver-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/simplewebserver.qcow2	debian	WdkJ7c40Z6uT
2016-03-03 17:36:42.407755	2016-03-03 17:36:42.407755	null	6f06b02b-6918-4acc-97f1-c67f9629709a	loadbalancer-VM-img	Image of the VNFC loadbalancer-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2	debian	R3L8uo725h1
2016-03-03 17:36:42.616141	2016-03-03 17:36:42.616141	null	8fec28f7-f8ed-449c-96b0-25fb8c131dfa	firewall-VM-img	Image of the VNFC firewall-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/firewall.qcow2	debian	P34T8Yui3o1Z
2016-03-03 17:36:42.835943	2016-03-03 17:36:42.835943	null	5ecae848-6134-4f3e-a372-8d141b35e315	webserver-VM-img	Image of the VNFC webserver-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/simplewebserver.qcow2	debian	WdkJ7c40Z6uT
2016-03-03 17:45:31.913664	2016-03-03 17:45:31.913664	null	e575755e-dbab-466c-9dab-574465ae177e	loadbalancer-VM-img	Image of the VNFC loadbalancer-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2	debian	R3L8uo725h1
2016-03-03 17:45:32.09215	2016-03-03 17:45:32.09215	null	eb39feb4-c869-4ca5-a508-7f376f54c4b9	firewall-VM-img	Image of the VNFC firewall-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/firewall.qcow2	debian	P34T8Yui3o1Z
2016-03-03 17:45:32.264864	2016-03-03 17:45:32.264864	null	d30dfde6-6ed9-4b82-8b5f-dd5de5dbc707	webserver-VM-img	Image of the VNFC webserver-VM	http://pg:decaf@groups.uni-paderborn.de/decaf/images/simplewebserver.qcow2	debian	WdkJ7c40Z6uT
\.


--
-- Data for Name: datacenter_images; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY datacenter_images (created_at, modified_at, meta, uuid, name, description, masta_image_id, image_id, datacenter_id) FROM stdin;
\.


--
-- Data for Name: vnfs; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY vnfs (created_at, modified_at, meta, uuid, name, description, path, max_instance, public, _class) FROM stdin;
2016-03-03 17:21:06.834441	2016-03-03 17:21:06.834441	null	5af986b9-1ed2-47b5-8bf3-c17acdc77272	loadbalancer	This is a virtual load balancer with one VM	/tmp/decaf/loadbalancer.vnfd	1	t	MISC
2016-03-03 17:26:28.124728	2016-03-03 17:26:28.124728	null	daca06a8-2247-419b-90b9-6d4647eb0fc8	loadbalancer	This is a virtual load balancer with one VM	/tmp/decaf/loadbalancer.vnfd	1	t	MISC
2016-03-03 17:29:08.748786	2016-03-03 17:29:08.748786	null	5d18a9dd-c3e0-4fa4-a25a-5d96173dbd6d	loadbalancer	This is a virtual load balancer with one VM	/tmp/decaf/loadbalancer.vnfd	1	t	MISC
2016-03-03 17:35:33.685284	2016-03-03 17:35:33.685284	null	16b91e2d-e637-4370-833c-bba18b9387bb	loadbalancer	This is a virtual load balancer with one VM	/tmp/decaf/loadbalancer.vnfd	1	t	MISC
2016-03-03 17:35:33.842685	2016-03-03 17:35:33.842685	null	43a61c91-65d2-49f4-aefc-ed57fcb7631b	firewall	This is a virtual firewall with one VM	/tmp/decaf/firewall.vnfd	1	t	MISC
2016-03-03 17:35:34.079542	2016-03-03 17:35:34.079542	null	caaa5986-cfa7-41d5-bce0-7bc25269a3d2	simplewebserver	This is a virtual webserver with one VM	/tmp/decaf/simplewebserver.vnfd	1	t	MISC
2016-03-03 17:36:42.424507	2016-03-03 17:36:42.424507	null	16160f71-9d68-4e58-99d0-0788460d7594	loadbalancer	This is a virtual load balancer with one VM	/tmp/decaf/loadbalancer.vnfd	1	t	MISC
2016-03-03 17:36:42.633813	2016-03-03 17:36:42.633813	null	9927457d-d17c-4f2b-b390-9a347d54f209	firewall	This is a virtual firewall with one VM	/tmp/decaf/firewall.vnfd	1	t	MISC
2016-03-03 17:36:42.868181	2016-03-03 17:36:42.868181	null	22a0d69b-89b0-403f-a582-9fbb506f03d9	simplewebserver	This is a virtual webserver with one VM	/tmp/decaf/simplewebserver.vnfd	1	t	MISC
2016-03-03 17:45:31.933291	2016-03-03 17:45:31.933291	null	beba0ec5-722a-4e8d-b4b5-4a94816e0897	loadbalancer	This is a virtual load balancer with one VM	/tmp/decaf/loadbalancer.vnfd	1	t	MISC
2016-03-03 17:45:32.108737	2016-03-03 17:45:32.108737	null	d7d5f994-adc4-4bd9-bc8d-3cc130457af9	firewall	This is a virtual firewall with one VM	/tmp/decaf/firewall.vnfd	1	t	MISC
2016-03-03 17:45:32.28212	2016-03-03 17:45:32.28212	null	d63d4f9e-8302-4764-8208-7cd85d02f1cf	simplewebserver	This is a virtual webserver with one VM	/tmp/decaf/simplewebserver.vnfd	1	t	MISC
\.


--
-- Data for Name: nets; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY nets (created_at, modified_at, meta, uuid, name, description, type, vnf_id) FROM stdin;
\.


--
-- Data for Name: vms; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY vms (created_at, modified_at, meta, uuid, name, description, vnf_id, max_instance, events, files, script_path, flavor_id, image_id, image_path) FROM stdin;
2016-03-03 17:21:06.868868	2016-03-03 17:21:06.868868	null	3855a3c8-8394-44c7-ac8d-c7bd25fb1d0f	loadbalancer-VM	Virtual machine containing loadbalancer image	5af986b9-1ed2-47b5-8bf3-c17acdc77272	1	{"new_successor": ["sudo server_add -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	da4ed525-194d-40b3-ba25-d79503e5b996	390b3b8b-c297-47ef-9d40-467cc614822b	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2
2016-03-03 17:26:28.140783	2016-03-03 17:26:28.140783	null	5607447d-37ce-4993-9e9b-b6d657706db0	loadbalancer-VM	Virtual machine containing loadbalancer image	daca06a8-2247-419b-90b9-6d4647eb0fc8	1	{"new_successor": ["sudo server_add -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	0881267a-987b-4642-8eef-831780cb98ed	ce785bfc-97fd-4c0e-88dd-02ba08303834	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2
2016-03-03 17:29:08.765788	2016-03-03 17:29:08.765788	null	fe63d345-6783-448a-8729-957e7a9c73f9	loadbalancer-VM	Virtual machine containing loadbalancer image	5d18a9dd-c3e0-4fa4-a25a-5d96173dbd6d	1	{"new_successor": ["sudo server_add -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	a51184f4-6e22-469d-9f9b-56b202e07e57	8a7d4c74-a577-47ee-bb01-4057db91a33e	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2
2016-03-03 17:35:33.702303	2016-03-03 17:35:33.702303	null	d3d3a045-4777-43ac-9bcb-113e4ea68564	loadbalancer-VM	Virtual machine containing loadbalancer image	16b91e2d-e637-4370-833c-bba18b9387bb	1	{"new_successor": ["sudo server_add -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	78d7f0b8-f17a-4491-abeb-c94d5a114842	4b5e626d-b2c0-494d-8412-ff7b6c0072d8	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2
2016-03-03 17:35:33.859256	2016-03-03 17:35:33.859256	null	fcce4852-0f60-493f-8a5d-7fc3ac4ffb88	firewall-VM	Virtual machine containing firewall image	43a61c91-65d2-49f4-aefc-ed57fcb7631b	1	{"new_successor": ["sudo new_successor -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	f1ca0b7e-c025-4043-b845-66740dd5a0c8	136def80-a484-4a2f-81e6-a0201acc428d	http://pg:decaf@groups.uni-paderborn.de/decaf/images/firewall.qcow2
2016-03-03 17:35:34.114091	2016-03-03 17:35:34.114091	null	8e82fe51-839f-4364-aabf-1bc98c00b463	webserver-VM	Generic Virtual Machine for webserver	caaa5986-cfa7-41d5-bce0-7bc25269a3d2	1	{"after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	dc4b4dd7-d656-4813-8883-4740fff1dabf	e43d828d-e338-408e-9de6-aaf8d6688c23	http://pg:decaf@groups.uni-paderborn.de/decaf/images/simplewebserver.qcow2
2016-03-03 17:36:42.44144	2016-03-03 17:36:42.44144	null	b74ba3b8-90f9-427b-b857-69e36b40c553	loadbalancer-VM	Virtual machine containing loadbalancer image	16160f71-9d68-4e58-99d0-0788460d7594	1	{"new_successor": ["sudo server_add -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	342e1e53-bc37-4015-9414-362b3803e9d3	6f06b02b-6918-4acc-97f1-c67f9629709a	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2
2016-03-03 17:36:42.666272	2016-03-03 17:36:42.666272	null	772e9454-0ab5-4440-a17f-3a2c48c9cd5d	firewall-VM	Virtual machine containing firewall image	9927457d-d17c-4f2b-b390-9a347d54f209	1	{"new_successor": ["sudo new_successor -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	41b7ff33-ddd1-46e4-ba90-9754868beef2	8fec28f7-f8ed-449c-96b0-25fb8c131dfa	http://pg:decaf@groups.uni-paderborn.de/decaf/images/firewall.qcow2
2016-03-03 17:36:42.901069	2016-03-03 17:36:42.901069	null	5cc2dff6-d4c1-4a27-a275-3d32e8857e5c	webserver-VM	Generic Virtual Machine for webserver	22a0d69b-89b0-403f-a582-9fbb506f03d9	1	{"after_startup": ["echo 'Starting'"]}	null	/tmp/decaf-vnf-manager/	be1ecbcf-18ff-420e-8765-771531a797f2	5ecae848-6134-4f3e-a372-8d141b35e315	http://pg:decaf@groups.uni-paderborn.de/decaf/images/simplewebserver.qcow2
2016-03-03 17:45:31.955694	2016-03-03 17:45:31.955694	null	579fd2d3-3ded-4ed3-9050-27e943661006	loadbalancer-VM	Virtual machine containing loadbalancer image	beba0ec5-722a-4e8d-b4b5-4a94816e0897	1	{"new_successor": ["sudo server_add -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	{}	/tmp/decaf-vnf-manager/	afe6260a-0f40-4a1a-b77e-e9d576117631	e575755e-dbab-466c-9dab-574465ae177e	http://pg:decaf@groups.uni-paderborn.de/decaf/images/loadbalancer.qcow2
2016-03-03 17:45:32.124514	2016-03-03 17:45:32.124514	null	f2157429-daf2-4c2c-a640-021c1a8bff2a	firewall-VM	Virtual machine containing firewall image	d7d5f994-adc4-4bd9-bc8d-3cc130457af9	1	{"new_successor": ["sudo new_successor -i {ip_address}"], "after_startup": ["echo 'Starting'"]}	{"test": "http://pg:decaf@groups.uni-paderborn.de/decaf/files/test.sh"}	/tmp/decaf-vnf-manager/	4453c898-4f1f-4d12-a1b6-1e6e83e3a021	eb39feb4-c869-4ca5-a508-7f376f54c4b9	http://pg:decaf@groups.uni-paderborn.de/decaf/images/firewall.qcow2
2016-03-03 17:45:32.306013	2016-03-03 17:45:32.306013	null	60bbf9c6-dde8-42ed-b07c-1ace988c6eaf	webserver-VM	Generic Virtual Machine for webserver	d63d4f9e-8302-4764-8208-7cd85d02f1cf	1	{"after_startup": ["echo 'Starting'"]}	{}	/tmp/decaf-vnf-manager/	666bc93e-6018-47d5-946f-c685cd5d4212	d30dfde6-6ed9-4b82-8b5f-dd5de5dbc707	http://pg:decaf@groups.uni-paderborn.de/decaf/images/simplewebserver.qcow2
\.


--
-- Data for Name: interfaces; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY interfaces (created_at, modified_at, meta, uuid, name, description, internal_name, external_name, vm_id, net_id, type, vpci, bw) FROM stdin;
2016-03-03 17:21:06.906358	2016-03-03 17:21:06.906358	null	e126bfa7-190c-44f6-96f2-9ec28b5bb49b	\N	\N	int0	mgmt0	3855a3c8-8394-44c7-ac8d-c7bd25fb1d0f	\N	mgmt	0000:00:09.0	1
2016-03-03 17:21:06.936836	2016-03-03 17:21:06.936836	null	5d44b6d5-bea2-4385-9cfd-eed8827b38f5	\N	\N	int1	data0	3855a3c8-8394-44c7-ac8d-c7bd25fb1d0f	\N	data	0000:00:11.0	10000
2016-03-03 17:21:06.953231	2016-03-03 17:21:06.953231	null	a23e7996-6c85-4373-8bf5-cfd109e1bb18	\N	\N	int2	data1	3855a3c8-8394-44c7-ac8d-c7bd25fb1d0f	\N	data	0000:00:12.0	10000
2016-03-03 17:26:28.155572	2016-03-03 17:26:28.155572	null	2ba27268-b840-4c78-94ba-c4d0f2157f5b	\N	\N	int0	mgmt0	5607447d-37ce-4993-9e9b-b6d657706db0	\N	mgmt	0000:00:09.0	1
2016-03-03 17:26:28.173807	2016-03-03 17:26:28.173807	null	ec7ebd2f-99aa-4037-b31e-7d9f1c5e6812	\N	\N	int1	data0	5607447d-37ce-4993-9e9b-b6d657706db0	\N	data	0000:00:11.0	10000
2016-03-03 17:26:28.1947	2016-03-03 17:26:28.1947	null	88c33975-08da-4dd2-afef-d60b0a838789	\N	\N	int2	data1	5607447d-37ce-4993-9e9b-b6d657706db0	\N	data	0000:00:12.0	10000
2016-03-03 17:29:08.782787	2016-03-03 17:29:08.782787	null	eb3449e7-4879-4249-b973-ad293d28f295	\N	\N	int0	mgmt0	fe63d345-6783-448a-8729-957e7a9c73f9	\N	mgmt	0000:00:09.0	1
2016-03-03 17:29:08.799824	2016-03-03 17:29:08.799824	null	a2b8d04d-a2c0-41d7-89c6-60c629fa3efb	\N	\N	int1	data0	fe63d345-6783-448a-8729-957e7a9c73f9	\N	data	0000:00:11.0	10000
2016-03-03 17:29:08.817767	2016-03-03 17:29:08.817767	null	ecd3fce5-923d-4970-8cff-b196529d913d	\N	\N	int2	data1	fe63d345-6783-448a-8729-957e7a9c73f9	\N	data	0000:00:12.0	10000
2016-03-03 17:35:33.718686	2016-03-03 17:35:33.718686	null	4d49dd42-2056-4f36-a50e-2d1bc7e442e4	\N	\N	int0	mgmt0	d3d3a045-4777-43ac-9bcb-113e4ea68564	\N	mgmt	0000:00:09.0	1
2016-03-03 17:35:33.734817	2016-03-03 17:35:33.734817	null	a2756adc-c631-4835-a215-0ab2ec2f589b	\N	\N	int1	data0	d3d3a045-4777-43ac-9bcb-113e4ea68564	\N	data	0000:00:11.0	10000
2016-03-03 17:35:33.751608	2016-03-03 17:35:33.751608	null	fe4c129e-d5dd-4aa7-86fc-59137e45c67d	\N	\N	int2	data1	d3d3a045-4777-43ac-9bcb-113e4ea68564	\N	data	0000:00:12.0	10000
2016-03-03 17:35:33.875819	2016-03-03 17:35:33.875819	null	74371670-5d2b-43ad-b6df-0c80fb94bc0c	\N	\N	int0	mgmt	fcce4852-0f60-493f-8a5d-7fc3ac4ffb88	\N	mgmt	0000:00:09.0	1
2016-03-03 17:35:33.892165	2016-03-03 17:35:33.892165	null	9a86fa1b-a5de-4fc0-b901-be5ce4d69555	\N	\N	int1	data0	fcce4852-0f60-493f-8a5d-7fc3ac4ffb88	\N	data	0000:00:11.0	10000
2016-03-03 17:35:33.909276	2016-03-03 17:35:33.909276	null	c1938245-5486-40cf-ad49-1e23513f821e	\N	\N	int2	data1	fcce4852-0f60-493f-8a5d-7fc3ac4ffb88	\N	data	0000:00:12.0	10000
2016-03-03 17:35:34.146479	2016-03-03 17:35:34.146479	null	7aa9f60a-881b-4854-b1c6-84ac7e88fdc8	\N	\N	int0	mgmt0	8e82fe51-839f-4364-aabf-1bc98c00b463	\N	mgmt	0000:00:11.0	1000
2016-03-03 17:35:34.179268	2016-03-03 17:35:34.179268	null	6c5db711-ea8d-46c5-9404-a42ee5fca3d2	\N	\N	int1	data0	8e82fe51-839f-4364-aabf-1bc98c00b463	\N	data	0000:00:11.0	10000
2016-03-03 17:36:42.473916	2016-03-03 17:36:42.473916	null	f3c305ec-9818-4faf-b74d-689a365ce821	\N	\N	int0	mgmt0	b74ba3b8-90f9-427b-b857-69e36b40c553	\N	mgmt	0000:00:09.0	1
2016-03-03 17:36:42.490152	2016-03-03 17:36:42.490152	null	c73ffc61-77cc-4e52-9357-c1faea9d3179	\N	\N	int1	data0	b74ba3b8-90f9-427b-b857-69e36b40c553	\N	data	0000:00:11.0	10000
2016-03-03 17:36:42.506651	2016-03-03 17:36:42.506651	null	741110fe-2c8d-434c-92ab-ac857380039b	\N	\N	int2	data1	b74ba3b8-90f9-427b-b857-69e36b40c553	\N	data	0000:00:12.0	10000
2016-03-03 17:36:42.699504	2016-03-03 17:36:42.699504	null	eeea3417-b88c-4da3-99b1-d8e1857ace41	\N	\N	int0	mgmt	772e9454-0ab5-4440-a17f-3a2c48c9cd5d	\N	mgmt	0000:00:09.0	1
2016-03-03 17:36:42.716502	2016-03-03 17:36:42.716502	null	7bc2e217-5878-4c2e-b1d6-dd8090c5af27	\N	\N	int1	data0	772e9454-0ab5-4440-a17f-3a2c48c9cd5d	\N	data	0000:00:11.0	10000
2016-03-03 17:36:42.748992	2016-03-03 17:36:42.748992	null	2400e0f7-3e27-4734-8c01-89ab0124aaa1	\N	\N	int2	data1	772e9454-0ab5-4440-a17f-3a2c48c9cd5d	\N	data	0000:00:12.0	10000
2016-03-03 17:36:42.934204	2016-03-03 17:36:42.934204	null	4e2fc43c-8ebe-4df1-8c07-7b0a4fdc13db	\N	\N	int0	mgmt0	5cc2dff6-d4c1-4a27-a275-3d32e8857e5c	\N	mgmt	0000:00:11.0	1000
2016-03-03 17:36:42.966169	2016-03-03 17:36:42.966169	null	8c6c9e1d-ef60-41fc-8c34-c766326567f0	\N	\N	int1	data0	5cc2dff6-d4c1-4a27-a275-3d32e8857e5c	\N	data	0000:00:11.0	10000
2016-03-03 17:45:31.973547	2016-03-03 17:45:31.973547	null	85c7218b-babd-446e-b46e-32d7ce249981	\N	\N	int0	mgmt0	579fd2d3-3ded-4ed3-9050-27e943661006	\N	mgmt	0000:00:09.0	1
2016-03-03 17:45:31.991326	2016-03-03 17:45:31.991326	null	4c7ba912-ddcd-42dd-a820-8d1f9981927c	\N	\N	int1	data0	579fd2d3-3ded-4ed3-9050-27e943661006	\N	data	0000:00:11.0	10000
2016-03-03 17:45:32.007945	2016-03-03 17:45:32.007945	null	36a6c2bc-6150-46a3-b931-4517a8e23584	\N	\N	int2	data1	579fd2d3-3ded-4ed3-9050-27e943661006	\N	data	0000:00:12.0	10000
2016-03-03 17:45:32.145934	2016-03-03 17:45:32.145934	null	3c30ae2a-f366-48a5-8ad2-49fac1836f22	\N	\N	int0	mgmt	f2157429-daf2-4c2c-a640-021c1a8bff2a	\N	mgmt	0000:00:09.0	1
2016-03-03 17:45:32.164623	2016-03-03 17:45:32.164623	null	479bc245-97fd-469c-9613-20bf6e6a55f4	\N	\N	int1	data0	f2157429-daf2-4c2c-a640-021c1a8bff2a	\N	data	0000:00:11.0	10000
2016-03-03 17:45:32.183505	2016-03-03 17:45:32.183505	null	2adaaf3a-20f4-45a6-9452-8f4600572e1b	\N	\N	int2	data1	f2157429-daf2-4c2c-a640-021c1a8bff2a	\N	data	0000:00:12.0	10000
2016-03-03 17:45:32.329835	2016-03-03 17:45:32.329835	null	8997dcbb-af28-4071-bce1-aabba50aca7e	\N	\N	int0	mgmt0	60bbf9c6-dde8-42ed-b07c-1ace988c6eaf	\N	mgmt	0000:00:11.0	1000
2016-03-03 17:45:32.356255	2016-03-03 17:45:32.356255	null	08ee612f-45cb-4dc0-8e55-560104eb36b6	\N	\N	int1	data0	60bbf9c6-dde8-42ed-b07c-1ace988c6eaf	\N	data	0000:00:11.0	10000
\.


--
-- Data for Name: scenarios; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY scenarios (created_at, modified_at, meta, uuid, name, description, public) FROM stdin;
\.


--
-- Data for Name: scenario_instances; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY scenario_instances (created_at, modified_at, meta, uuid, name, description, scenario_id) FROM stdin;
\.


--
-- Data for Name: vnf_instances; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY vnf_instances (created_at, modified_at, meta, uuid, name, description, scenario_instance_id, vnf_id, datacenter_id) FROM stdin;
\.


--
-- Data for Name: net_instances; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY net_instances (created_at, modified_at, meta, uuid, name, description, type, vnf_instance_id, net_id) FROM stdin;
\.


--
-- Data for Name: vm_instances; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY vm_instances (created_at, modified_at, meta, uuid, name, description, vnf_instance_id, vm_id) FROM stdin;
\.


--
-- Data for Name: interface_instances; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY interface_instances (created_at, modified_at, meta, uuid, name, description, internal_name, external_name, vm_instance_id, net_instance_id, interface_id, type, vpci, bw, physical_name, ip_address) FROM stdin;
\.


--
-- Data for Name: scenario_nets; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY scenario_nets (created_at, modified_at, meta, uuid, name, description, type, scenario_id) FROM stdin;
\.


--
-- Data for Name: scenario_vnfs; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY scenario_vnfs (created_at, modified_at, meta, uuid, name, description, public, scenario_id, vnf_id, graph) FROM stdin;
\.


--
-- Data for Name: scenario_interfaces; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY scenario_interfaces (created_at, modified_at, meta, uuid, name, description, scenario_vnf_id, scenario_net_id, interface_id, public) FROM stdin;
\.


--
-- Data for Name: scenario_net_instances; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY scenario_net_instances (created_at, modified_at, meta, uuid, name, description, type, scenario_net_id, scenario_instance_id) FROM stdin;
\.


--
-- Data for Name: scenario_interface_instances; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY scenario_interface_instances (created_at, modified_at, meta, uuid, name, description, vnf_instance_id, scenario_net_instance_id, interface_instance_id, scenario_interface_id) FROM stdin;
\.


--
-- Data for Name: vm_instance_keypairs; Type: TABLE DATA; Schema: public; Owner: pgdecaf
--

COPY vm_instance_keypairs (created_at, modified_at, meta, uuid, name, description, vm_instance_id, keypair_id, private_key, public_key, fingerprint, username, password) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

