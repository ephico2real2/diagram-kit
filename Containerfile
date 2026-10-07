# A Linux with the kit and its Chromium, as a CI runner has them: to see a diagram page as the check-diagrams job
# sees it, from a Mac. Since 0.2.3 the two draw text at the same widths; this is for the day a page passes on the Mac
# and fails in CI all the same.
#
#   podman build --build-arg KIT_REF=v0.2.4 -t diagram-kit-linux .
#   podman run --rm -v "$PWD":/repo:ro diagram-kit-linux --check docs/diagrams/<slug>/source.html
#
# KIT_REF is a tag or a branch of this repository. The entry point is diagram-render; the repository is mounted
# read-only at /repo, the working directory, so --check is the mode to use.
FROM docker.io/library/python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
ARG KIT_REF
RUN test -n "${KIT_REF}" || { echo "give --build-arg KIT_REF=<tag or branch>" >&2; exit 1; }
RUN pip install --no-cache-dir "diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@${KIT_REF}" \
    && python -m playwright install --with-deps chromium
WORKDIR /repo
ENTRYPOINT ["diagram-render"]
