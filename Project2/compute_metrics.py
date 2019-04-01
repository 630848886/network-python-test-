import sys
import os
import glob

print "Called compute() function in compute_metrics.py"

import sys
import os
import glob


class Package:
    def __init__(self):
        self.time = .0
        self.src = ''
        self.dst = ''
        self.len = 0
        self.type = 0
        self.seq = 0

    def __str__(self):
        return "time: %f, src: %s, dst: %s, len: %d, type: %d, seq: %d" % \
               (self.time, self.src, self.dst, self.len, self.type, self.seq)


class MetricsCalculator:

    def __init__(self, packages, self_ip):
        self.addr = self_ip

        self.requests = {}
        self.replies = {}
        self.packages = packages

        # request package save into self.requests, reply save into self.replies
        for package in packages:
            if package.type == 8:
                # seq exist. change to another seq
                if package.seq in self.requests.keys():
                    package.seq <<= 16
                self.requests[package.seq] = package
            elif package.type == 0:
                # seq exist. change to another seq
                if package.seq in self.replies.keys():
                    package.seq <<= 16
                self.replies[package.seq] = package
            else:
                # TODO find another type
                continue

    def echo_requests_sent_num(self):
        result = 0
        for package in self.requests.values():
            if package.src == self.addr:
                result += 1

        return result

    def echo_requests_recv_num(self):
        result = 0
        for package in self.requests.values():
            if package.dst == self.addr:
                result += 1

        return result

    def echo_replies_sent_num(self):
        result = 0
        for package in self.replies.values():
            if package.src == self.addr:
                result += 1

        return result

    def echo_replies_recv_num(self):
        result = 0
        for package in self.replies.values():
            if package.dst == self.addr:
                result += 1

        return result

    def echo_requests_bytes_sent(self):
        result = 0
        for package in self.requests.values():
            if package.src == self.addr:
                result += package.len

        return result

    def echo_requests_bytes_recv(self):
        result = 0
        for package in self.requests.values():
            if package.dst == self.addr:
                result += package.len

        return result

    def echo_requests_data_sent(self):
        result = 0
        for package in self.requests.values():
            if package.src == self.addr:
                result += package.len - 42

        return result

    def echo_requests_data_recv(self):
        result = 0
        for package in self.requests.values():
            if package.dst == self.addr:
                result += package.len - 42

        return result

    def average_rtt(self):
        result = .0
        counter = 0

        for seq, package in self.requests.items():
            if seq not in self.replies.keys():
                # TODO reply not found
                continue
            if package.src != self.addr:
                # request from other node
                continue

            result += self.replies[seq].time - package.time
            counter += 1

        if counter != 0:
            return result * 1000 / counter
        else:
            return .0

    def echo_requests_througput(self):
        return float(self.echo_requests_bytes_sent()) / (self.average_rtt() * self.echo_requests_sent_num())

    def echo_requests_goodput(self):
        return float(self.echo_requests_data_sent()) / (self.average_rtt() * self.echo_requests_sent_num())

    def average_reply_delay(self):
        result = .0
        counter = 0

        for seq, package in self.requests.items():
            if seq not in self.replies.keys():
                # TODO reply not found
                continue
            if package.dst != self.addr:
                # request sent to this node
                continue

            result += self.replies[seq].time - package.time
            counter += 1

        if counter != 0:
            return result * 1000 / counter
        else:
            return .0

    def average_num_of_hops(self):
        hops = 0

        same = 0
        diff = 0
        for request in self.requests.values():
            if (request.src != self.addr):
                continue
            src_subnet = request.src[: request.src.rfind('.')]
            dst_subnet = request.dst[: request.dst.rfind('.')]
            if src_subnet == dst_subnet:
                hops += 1
                same += 1
            else:
                hops += 3
                diff += 1

        return float(hops) / (same + diff)


def read_file(filename):
    packages = []
    with open(filename) as fp:
        for line in fp:
            line = line.replace(',', '')
            data = line.strip().split()

            package = Package()
            package.time = float(data[1])
            package.src = str(data[2])
            package.dst = str(data[3])
            package.len = int(data[5])
            package.seq = int(data[10][data[10].rfind('/') + 1:])
            if str(data[8]) == 'reply':
                package.type = 0
            else:
                package.type = 8

            packages.append(package)

    return packages


def write_csv(node_name, metrics_calculator, filename):
    with open(filename, 'a') as fp:
        fp.write(node_name + '\r\n')
        fp.write('\r\n')

        fp.write('Echo Requests Sent,Echo Requests Received,Echo Replies Sent,Echo Replies Received\r\n')
        fp.write('%d,%d,%d,%d\r\n' %
                 (metrics_calculator.echo_requests_sent_num(),
                  metrics_calculator.echo_requests_recv_num(),
                  metrics_calculator.echo_replies_sent_num(),
                  metrics_calculator.echo_replies_recv_num()))
        fp.write('Echo Request Bytes Sent (bytes),Echo Request Data Sent (bytes)\r\n')
        fp.write('%d,%d\r\n' %
                 (metrics_calculator.echo_requests_bytes_sent(), metrics_calculator.echo_requests_data_sent()))
        fp.write('Echo Request Bytes Received (bytes),Echo Request Data Received (bytes)\r\n')
        fp.write('%d,%d\r\n' %
                 (metrics_calculator.echo_requests_bytes_recv(), metrics_calculator.echo_requests_data_recv()))
        fp.write('\r\n')
	# Format the decimals correctly to round and display either 1 or 2 decimal places
        fp.write('Average RTT (milliseconds),%.2f\r\n' % round(metrics_calculator.average_rtt(),2))
        fp.write('Echo Request Throughput (kB/sec),%.1f\r\n' % round(metrics_calculator.echo_requests_througput(),1))
        fp.write('Echo Request Goodput (kB/sec),%.1f\r\n' % round(metrics_calculator.echo_requests_goodput(),1))
        fp.write('Average Reply Delay (us),%.2f\r\n' % round((metrics_calculator.average_reply_delay() * 1000),2))
        fp.write('Average Echo Request Hop Count,%.2f\r\n' % round(metrics_calculator.average_num_of_hops(),2))
        fp.write('\r\n')


def compute():
    csv_filename = 'compute_result.csv'
    node_ips = ['192.168.100.1',
                '192.168.100.2',
                '192.168.200.1',
                '192.168.200.2']

    # Remove any previously existing csv file
    for filename in glob.glob(csv_filename):
        os.remove(filename)

    for i in range(1, 5):
        node_name = 'Node %d' % i
        node_filename = 'Node%d_filtered.txt' % i

        # parse file, get Node i 's echo package
        packages = read_file(node_filename)
        # compute
        calculator = MetricsCalculator(packages, node_ips[i - 1])
        # add results to result csv file
        write_csv(node_name, calculator, csv_filename)


def main(argv):
    compute()


if __name__ == '__main__':
    main(sys.argv)


