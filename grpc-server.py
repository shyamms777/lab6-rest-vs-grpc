#!/usr/bin/env python3

from concurrent import futures
import argparse
import base64
import io

import grpc
from PIL import Image

import lab6_pb2
import lab6_pb2_grpc


def imageSize(imgBytes):
    try:
        img = Image.open(io.BytesIO(imgBytes))
        return lab6_pb2.imageReply(width=img.size[0], height=img.size[1])
    except Exception:
        return lab6_pb2.imageReply(width=0, height=0)


class Lab6Servicer(lab6_pb2_grpc.Lab6Servicer):

    def Add(self, request, context):
        return lab6_pb2.addReply(sum=request.a + request.b)

    def RawImage(self, request, context):
        return imageSize(request.img)

    def DotProduct(self, request, context):
        if len(request.a) != len(request.b):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                          "vectors a and b must be of the same length")
        dot = sum(x * y for x, y in zip(request.a, request.b))
        return lab6_pb2.dotProductReply(dotProduct=dot)

    def JsonImage(self, request, context):
        return imageSize(base64.b64decode(request.img))


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    lab6_pb2_grpc.add_Lab6Servicer_to_server(Lab6Servicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on port {port}")
    server.wait_for_termination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gRPC server')
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=50051,
        help='Port on which to run the server (default: 50051)'
    )
    args = parser.parse_args()
    serve(args.port)