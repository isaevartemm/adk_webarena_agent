# Capstone project - WebArena MVP agent with google ADK

## The pitch:

Hello, I'm an independent researcher, lately I've been experimenting with Webarena benchmark for evaluating Agent browsing capability in fixed envirinment. But the repo was about 10000 lines of code and not very reliable. So I decided to try to replicate its fuctionality with Google ADK. And here is my mock.

## Core concept and value:

So when I started this project I saw dozens MCP options for data crawling, unfortunately none of them worked with my self-hosted benchmark webistes (probably of http path) so I wrote my own data crawling tools and imtegrated them with agent capabilities. 

The agent have two main functions - page description and action performance (like clicking buttons or links). With this setup I've been able to quickle finish first experiments and now planning to extend research. I also added additional logging to each of functions

## Setup:

1) setup webarena websites (or use mine, I'll make them available for a couple of days after submission - http://158.160.91.48:4399)
2) ```adk web --port 8000``` or ```adk run my_agent```

# Results:

Here I'll leave some screenshots of what was achieved when testing. As you can see the Agent is able to successfully navigate through tree of links and extract price of the goods from second website.

![img.png](img.png)


Start page:
![Снимок экрана 2025-12-01 в 22.41.50.png](..%2F..%2F..%2F..%2Fvar%2Ffolders%2Fqq%2Fn90xld6122xd2l8p1gnwt25r0000gn%2FT%2FTemporaryItems%2FNSIRD_screencaptureui_52UwHf%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-12-01%20%D0%B2%2022.41.50.png)

Seconary page:
![Снимок экрана 2025-12-01 в 22.43.00.png](..%2F..%2F..%2F..%2Fvar%2Ffolders%2Fqq%2Fn90xld6122xd2l8p1gnwt25r0000gn%2FT%2FTemporaryItems%2FNSIRD_screencaptureui_1yEoJP%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-12-01%20%D0%B2%2022.43.00.png)