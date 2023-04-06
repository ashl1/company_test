# To talk:

# Parsing

* network error retrying
* parsing error limiting
* redirects handling
* CSRF for each request
* JS: Button opened URL
* Forms?
* robots.txt
* Google Sitemap
* proper User Agent and referer url
* http body encoding (brotli, for example)
* parse big HTML pages by chunks? 

# Load and durability

* 1 IP connections pool limit (65k) + bandwidth limit
* rate limiting to (sub)domain required by server
  * limiting itself with random
  * transparent proxy/VPN
  * pool of IPs
* loop detection
  * store in RAM
  * prefix tree
  * key-value DB
* ignore HTTP params values (all, not all), protocol, port, #
* limiting URLs to another domain
* permanent storage (all writes/by interval)

# Extension
* parse urls from text documents, PDF
* URLs to images and any other media and document
* detect similar/same medias (i.e. image are same but in different extension, resolution, size)
* load and execute JS scripts (to use in SPA, detect dynamic urls)
* account based crawling (use account credentials)
* auto captcha resolving by another services
* don't walk to links not accessible by user but acessible programmatically (bot mitigation)
* API get current status of process (number of URIs, loop detects, csrf detects, ignored, ...)
* re-visit pages to actualize data
* valid URI not just URL detection
* the system as a service not just script

# Cloud
* AWS
* GCP
* Azure
* any other with docker-compose
* self-hosted requirements (network, pc)


# Urgent TODO
Return found URLs added after specified time

# How parse now
* get by '' and by ""
* Regexp? Ignore XML or HTML markup
* <a href=''
