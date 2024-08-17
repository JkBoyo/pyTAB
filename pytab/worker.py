#!/usr/bin/env python3

# pytab.worker.py
# A transcoding hardware benchmarking client (for Jellyfin)
#    Copyright (C) 2024 BotBlake <B0TBlake@protonmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##########################################################################################

import concurrent.futures
import re
import subprocess

import click


def run_ffmpeg(pid: int, ffmpeg_cmd: list) -> tuple:  # Process ID,
    # click.echo(f"{pid} |> Running FFMPEG Process: {pid}")
    timeout = 120  # Stop any process that runs for more then 120sec
    failure_reason = None
    try:
        process_output = subprocess.run(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            capture_output=True,
            universal_newlines=True,
            timeout=timeout,
        )

        retcode = process_output.returncode
        ffmpeg_stderr = process_output.stderr

        if retcode > 0:
            click.echo(f"ERROR: {ffmpeg_stderr}")  # <- Silencing Output
            failure_reason = "generic_ffmpeg_failure"  # <-- HELP WANTED!

    except subprocess.TimeoutExpired:
        ffmpeg_stderr = 1
        failure_reason = "failed_timeout"

    except Exception as e:
        click.echo(e)
        exit(1)

    # click.echo(f"{pid} >| Ended FFMPEG Run: {pid}")
    return ffmpeg_stderr, failure_reason


def workMan(worker_count: int, ffmpeg_cmd: str) -> tuple:
    ffmpeg_cmd_list = ffmpeg_cmd.split()
    raw_worker_data = {}
    failure_reason = None
    # click.echo(f"> Run with {worker_count} Processes")
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(run_ffmpeg, nr, ffmpeg_cmd_list): nr
            for nr in range(worker_count)
        }
        for future in concurrent.futures.as_completed(futures):
            pid = futures[future]
            try:
                raw_worker_data[pid] = future.result()
                # click.echo(f"> > > Finished Worker Process: {pid}")
                if raw_worker_data[pid][1]:
                    failure_reason = raw_worker_data[pid][1]
            except Exception as e:
                print(f"Worker {pid} generated an exception: {e}")

    if failure_reason:
        raw_worker_data = None
        # Deleting all the Raw Data, since run with failed Worker is not counted

    run_data_raw = []
    if raw_worker_data:  # If no run Failed
        for pid in range(worker_count):
            process_output = raw_worker_data[pid][0]

            framelines = []
            rtime = 0.0
            for line in process_output.split("\n"):
                if re.match(r"^frame=", line):
                    if re.match(r"frame=\s*([5-9]\d{2,}|[1-9]\d{3,})", line):
                        new_line = re.sub(r"=\s*", "=", line)
                        framelines.append(new_line)  # framelines (Frame>500)

                if re.match(r"^bench: maxrss", line):
                    rssline = line.split()
                    workrss = float(
                        rssline[1].split("=")[-1].replace("kB", "")
                    )  # maxrss

                if re.match(r"^bench: utime", line):
                    timeline = line.split()
                    rtime = float(timeline[3].split("=")[-1].replace("s", ""))  # rtime

            frames = []
            speeds = []
            framerates = 0
            for line in framelines:
                new_line = line.split()
                frames.append(int(float(new_line[0].split("=")[-1])))
                framerates += int(float(new_line[1].split("=")[-1]))
                speeds.append(float(new_line[6].split("=")[-1].replace("x", "")))
            lineAmmount = len(framelines)
            if lineAmmount == 0:
                lineAmmount = 1
            if len(frames) == 0:
                frames.append(1)

            avgSpeed = sum(speeds) / lineAmmount
            maxFrame = max(frames)
            avgFPS = framerates / lineAmmount

            worker_data = {
                "frame": maxFrame,
                "speed": avgSpeed,
                "time_s": rtime,
                "rss": workrss,
                "FPS": avgFPS,
            }

            run_data_raw.append(worker_data)
        return False, evaluateRunData(run_data_raw)
    else:
        return True, failure_reason


def evaluateRunData(run_data_raw: list) -> dict:
    workers = len(run_data_raw)

    total_time = 0
    total_speed = 0
    total_fps = 0
    frames = []
    rss_kbs = []
    for worker_data in run_data_raw:
        total_time += worker_data["time_s"]
        total_speed += worker_data["speed"]
        total_fps += worker_data["FPS"]
        frames.append(worker_data["frame"])
        rss_kbs.append(worker_data["rss"])
    max_Frame = max(frames)
    max_rss = max(rss_kbs)
    avgTime = total_time / workers
    avgSpeed = total_speed / workers
    avgFPS = total_fps / workers

    run_data_eval = {
        "workers": workers,
        "frame": max_Frame,
        "speed": avgSpeed,
        "time_s": avgTime,
        "rss_kb": max_rss,
        "avgFPS": avgFPS,
    }
    return run_data_eval
