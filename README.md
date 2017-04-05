# NASA Fan Website Traffic Data: Basic Analytics and Security Measures

## Introduction

This repo performs basic analytics on the server log file, which corresponds to the Internet traffic data that is generated from a NASA fan website. The analysis carried out here emphasize more on algorithm efficiency, according to the spirit of the Insight 2017 code challenge (the detailed description of the challenge is [here](https://github.com/InsightDataScience/fansite-analytics-challenge)). 

## Language

The language used is Python3. Dependent libraries includes `re`, `datetime` and `collections`.

## Algorithm

### Basic structure of the cleaned data

- A list of individual login records are generated, with each record as a python dictionary which includes the following features:
    - **raw**: 199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245
    - **host**: 199.72.81.55
    - **time**: 01/Jul/1995:00:00:01 -0400
    - **request**:[/history/apollo/]
    - **code**: 200
    - **bytes**: 6245
- A robust way of splitting each record is defined
    - original record is first splitted into 3 substrings, by <span style="color:red">"["</span> and <span style="color:red">"]"</span>
    - the substrings are further splitted by <span style="color:red">"[[:space:]]"</span>
- Since the split on string is performed twice, the overall computational complexity is `2*size(log file)`
- In general, the list of dictionaries functions the same way as a pandas data frame

### Generating rank lists: Host ID and Resources

To generate a rank list of items of certain features from the clean data, another dictionary is created. The keys of the new dictionary correspond to unique items within that feature and the values indicate their times of appearance. The list of top-10 items are obtained by sorting the dictionary values in descending orders. The overall computation complexity is `O(n+nlog(n)`.

### Busiest 60-minute periods

**Two loops (mimic two pointers)** are used to sweep the whole list of entries. The first loop goes over individual entries. The second loop searches the corresponding entry when the 60-minute time window ends. Since the second loop does not go over the whole list each time, the computation complexity is larger but close to `O(n)` and less than `O(n^2)`.

### Blocking items

A **while loop** and a variable **"count"** are used to finish the task. We sweep the list with the while loop, and start to count when a failed login appears. If during the 20-seconds window, we obtain 3 blocked login, then we start blocking the subsequent logins (no matter if they are successful or not) within next 5-minute window. The list items that are already dealt with will be removed from the list after each iteration.

### Additional features

Feature 4 (Blocking items) has some drawbacks, that is if the blocked host is not logging in for the next 5 minutes, then there is no records of the blocking event. To compensate for that, one additional feature is generated (named *blocked hosts*). This feature will give  a list of all the blocking events that indeed happened, with the corresponding host id and the time when blocking happens. An example is given in the following:

e.g., `blocked_host.txt`:

      199.72.81.55,01/Jul/1995:00:00:12 -0400
      ...



