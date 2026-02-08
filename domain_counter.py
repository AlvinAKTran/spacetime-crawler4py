import sys
import re
from pathlib import Path
from urllib.parse import urlparse


def domain_counter(log_path: Path) -> tuple[set, dict]:
    unique_pages = set()
    subdomains = dict()

    with open(log_path, 'r') as logs:
        for index, line in enumerate(logs):
            try:
                url_string = re.search(r'https?:\/\/[^\s,]+', line)

                if url_string:
                    url = urlparse(url_string.group(0))
                    try:
                        if url.geturl().removesuffix(url.fragment) in unique_pages:
                            print(f"Duplicate URL found in line {index + 1}. Skipping.")
                        else:
                            subdomains[url.netloc.lower()] += 1
                    except KeyError:
                        subdomains[url.netloc.lower()] = 1

                    unique_pages.add(url.geturl().removesuffix(url.fragment))
                else:
                    print(f"Could not find URL in line {index + 1}. Skipping.")
            except Exception as e:
                print(f"Error processing line {index + 1}: {e}. Skipping.")
    
    return unique_pages, subdomains


def main() -> None:
    log_path = Path(sys.argv[1])
    unique_pages, subdomains = domain_counter(log_path)

    print(f"Total unique pages: {len(unique_pages)}\n")
    print(f"Number of subdomains: {len(subdomains)}\n")

    urls_counted = 0
    for subdomain, count in sorted(subdomains.items()):
        print(f"{subdomain}, {count}")
        urls_counted += count

    if urls_counted != len(unique_pages):
        print(f"\nWarning: {len(unique_pages) - urls_counted} URLs not counted")

if __name__ == "__main__":
    main()