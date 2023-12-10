import argparse
import grpc
from reddit_service import RedditService

def serve(host, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    redditDataModel.add_RedditServiceServicer_to_server(RedditService(), server)
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reddit Clone gRPC Server')
    parser.add_argument('--host', default='localhost', help='Host to serve on')
    parser.add_argument('--port', type=int, default=50051, help='Port to serve on')
    args = parser.parse_args()

    serve(args.host, args.port)
