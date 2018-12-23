# nofollow_finder 1.0.0

A tool that finds links with rel="nofollow" attribute on the web and 
generates a CSV report.


## Workflow

1. **Input - URLs**

    Input in a CSV file with a list of URLs.

    This file contains a list of URLs tha the script will download. They 
    have to be present in the first column of the file. Other columns 
    are ignored.

2. **Input - domains**

    Domains are specified via CLI parameter. They have to be separated 
    by comma and without any spaces.

3. **Download a URL**

    The first URL in the input file will be downloaded. Download happens 
    using `curl` tool.

    It will follow HTTP redirects automatically, unless told not to (see
    CLI options).

    Only pages that return with HTTP status code `200` will be processed.

4. **Parse**

    The download HTML is parsed for A tags that point to one of the
    domains specified in "2.".

    Every such tag is logged.

    The tool counts how many of these tags have rel="nofollow" attribute.

5. **Output a line**

    The tool outputs a CSV line into the specified output CSV file.

6. **Repeat**

    The tool takes the next URL from the list in "1." and proceeds to "3.".


## Setup

### Requirements

This tool has been tested under:

Python:
 * 2.7.15

OS: 
 * Mac 10.14.2 "Mojave"
 * Ubuntu 16.04.4 LTS "Xenial Xerus"

It should work on all POSIX systems.


### Create a virtual environment

Optional but recommended.

#### Virtualenv with pyenv

[pyenv](https://github.com/pyenv/pyenv) is a modern tool for managing 
multiple Python environments effectively.

```bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

# if on a Mac, use ~/.bash_profile
echo "" >> ~/.bashrc
echo "# pyenv" >> ~/.bashrc
echo "export PATH=\"$(echo ${HOME})/.pyenv/bin:$PATH\"" >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

source ~/.bashrc

pyenv install 2.7.15
pyenv virtualenv 2.7.15 nofollow_finder

mkdir -p src/nofollow_finder
cd src/nofollow_finder
pyenv local nofollow_finder
```

You should see `(nofollow_finder) ` prepended to your usual shell prompt.

Every time you "cd into" the project directory, the virtualenv will be 
automatically activated. When "cd out of" the directory, it will be 
deactivated.

To activate the virtualenv manually: `pyenv activate nofollow_finder`

The name of the virtualenv does not have to match the name of this tool.

It is possible to run `pyenv local nofollow_finder` in multiple directories
in different locations, e.g. in:
```
/home/myname/src/nofollow_finder
/home/myname/documents/seo_efforts
```

Also note that it is not necessary to run the command in any 
sub-directories, as they will "inherit" the configuration is present in 
any parent directory. 


#### Installation

Get a GitHub personal token from [https://github.com/settings/tokens](https://github.com/settings/tokens).

Then run:
```bash
export GH_USER="YOUR_USERNAME"
curl -u"$GH_USER" -L -O https://github.com/frnhr/nofollow_finder/archive/1.0.0.tar.gz

# paste your token

tar -xvzf 1.0.0.tar.gz

cd nofollow_finder-1.0.0/ 
pip install .
````


#### Test

Test that all is working well.

```bash
$ nofollow_finder -v
nofollow_finder 1.0.0
```

Run the provided sample CSV, and expect output like below (trimmed for clarity).

```bash
$ nofollow_finder -d twitter.com,facebook.com -i SampleLinks.csv
https://example.com/,200,No,0
ERROR     ...  curl returned error code 6 for http://doesnotexist.fooo
http://doesnotexist.fooo,0,Fail,0
INFO      ...   https://en.wikinews.org/wiki/Main_Page...
...
INFO      ...   https://en.wikinews.org/wiki/Main_Page
...
https://en.wikinews.org/wiki/Main_Page,200,Yes,2
ERROR     ...  HTTP status 503 for url http://changeset.hr/
http://changeset.hr/,0,Fail,0
ERROR     ...   unexpected error while downloading url http://google.com
http://google.com,0,Fail,0
ERROR     ...   No A nodes found on http://changeset.hr/misc/noancors.html
http://changeset.hr/misc/noancors.html,200,No,0
```


## CLI usage

For a full description of available options, run `nofollow_finder --help`.

### Common usage

```
nofollow_finder -d twitter.com,facebook.com -i input.csv -o output.csv -l finder.log
```

This will:
 * read input URLs from `input.csv` file,
 * write CSV report to `output.csv` file,
 * and write logs to `finder.log` file. 


### Logging to screen

If `-l` option is not provided, the logs will be written to standard output.
This will make them visible on the terminal.

```
nofollow_finder -d twitter.com,facebook.com -i input.csv -o output.csv
```

This will:
 * read input URLs from `input.csv` file,
 * write CSV report to `output.csv` file,
 * write logs **standard error** stream (visible in terminal). 


### Logging to screen and to file

```
nofollow_finder -d twitter.com,facebook.com -i input.csv -o output.csv 2>&1 | tee finder.log
```

This will:
 * read input URLs from `input.csv` file,
 * write CSV report to `output.csv` file,
 * write logs **standard output** stream (visible in terminal),
 * write logs to `finder.log` file. 


### Report to screen and file, logging to screen

```
nofollow_finder -d twitter.com,facebook.com -i input.csv | tee output.csv
```

This will:
 * read input URLs from `input.csv` file,
 * write CSV report to `output.csv` file,
 * write logs **standard error** stream (visible in terminal),
 * write CSV report to **standard error** stream (visible in terminal).


### Take input from multiple CSV files

```
cat first.csv second.csv | nofollow_finder -d twitter.com,facebook.com
```

This will:
 * read input URLs from `first.csv` and `second.csv` files,
 * write logs **standard error** stream (visible in terminal),
 * write CSV report to **standard error** stream (visible in terminal).

Providing `-d` and `-l` options can redirect output and log to files just 
like before. Any other combination from examples above can be used as well.


## Gotchas

### Sub-domains

Given a domain, the tool will find all links pointing to URLs on that domain
plus any subdomain, e.g:

```
# this finds links to twitter.com AND www.twitter.com AND www.en.twitter.com:
nofollow -d twitter.com
```

The tool will not work "backwards", so that if a sub-domain is given, it
will not find links to root domain, e.g: 
```
# this finds links to www.twitter.com AND www.en.twitter.com BUT NOT to twitter.com:
nofollow -d www.twitter.com
```


### Domains are case-insensitive

These all produce identical results:

```bash
nofollow_filter -d twitter.com
nofollow_filter -d TWITTER.com
nofollow_filter -d Twitter.COM
nofollow_filter -d Twitter.coM
```
