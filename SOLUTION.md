# Lab 6 Solution: REST vs gRPC

Times are milliseconds per operation, measured from `lab6-client` (`us-west1-a`) using internal IPs. Local used `127.0.0.1/localhost`, Same-Zone used a second VM in `us-west1-a`, and Different Region used a VM in `europe-west3-a` (Frankfurt). PING is the average of 20 pings.

| Method | Local | Same-Zone | Different Region |
|---|---|---|---|
| REST add | 2.79 | 3.42 | 333.47 |
| gRPC add | 0.78 | 1.14 | 145.80 |
| REST rawimg | 5.21 | 9.20 | 1354.46 |
| gRPC rawimg | 12.72 | 13.84 | 183.76 |
| REST dotproduct | 3.12 | 4.30 | 332.50 |
| gRPC dotproduct | 0.87 | 1.36 | 164.51 |
| REST jsonimg | 27.57 | 31.56 | 1460.04 |
| gRPC jsonimg | 28.79 | 28.01 | 217.52 |
| PING | 0.045 | 0.440 | 141.44 |

## Observations

On the same machine and within one zone, the network barely matters (ping is under half a millisecond), so what I measured is mostly software overhead. gRPC was about 3 times faster for the small calls, since REST has to set up a connection, send headers and parse JSON every time. REST was actually faster for the raw image locally (5 ms vs 13 ms), so gRPC isn't automatically faster for big payloads.Locally, REST was faster for the 1.6 MB image because gRPC’s per-byte overhead (framing and copying data between its layers) outweighed REST’s per-call connection setup. Across regions, that overhead becomes negligible compared with round trips, and gRPC is faster.

For Frankfurt every round trip costs about 141 ms. gRPC `add` took 146 ms, basically one round trip, because its single TCP connection is already open. REST `add` took 333 ms, since each query opens a new connection and pays an extra round trip for the TCP handshake before the request can even go out. Sending 100 numbers as JSON instead of two in the URL made no difference (`dotproduct` also took 333 ms). The image tests showed the biggest gap, REST was 7 times slower (1354 ms vs 184 ms). TCP has a slow start as a new connection starts by sending a little data and speeds up each round trip, so REST needed about 9 round trips to upload 1.6 MB, while gRPC's connection was already up to speed. Overall, the closer the client and server are, the less the protocol matters. Far apart, reusing a connection is what makes gRPC faster.
