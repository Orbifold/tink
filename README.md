
# Tink

Natural language understanding module for English and Dutch in particular.

English is widely supported by NLP frameworkds but Dutch, being a very small group of people on a planetary scale, is hardly around. [Spacy v2.0](http://spacy.io) does have some support but fails rather miserably when it comes to dependency parsing. Also, things like dictionaries and synonyms are hard to find. There is of course [Frog](http://languagemachines.github.io/frog/) but it's a total abomination and as good as impossible to build. Running it in a docker container is pretty much the only option and creates an unnecessary liability.

This project collects various bits which were created for diverse consultancy projects. It's not perfect but does the job and you will find some bits you won't find elsewhere; pattern matching and semantic utilities.

## References and pointers

The Dutch thesaurus is obtained from [OpenTaalBank](http://data.opentaal.org/opentaalbank/thesaurus/). It's not very complete but has the merrit that you can edit it as plain text file.

The core language knowledge is based on [UDPipe](https://ufal.mff.cuni.cz/udpipe/users-manual#run_udpipe_input) and it would not be too difficult to extend the current code to another 80 languages supported by UDPipe.

A lot of [good stuff](https://github.com/bnosac) comes from the Belgian BMOSAC company's open source efforts you can find on Github. Their [R-package wrapping UDPipe](https://github.com/bnosac/udpipe) in particular replaces the ugly Frog machine.
The Python binding to UDPipe is a thin wrapper around the C++ interface and makes it difficult to figure out how to use it. Some info [is available here](https://github.com/ufal/udpipe/tree/master/bindings/python/examples) but see the code is something like this

        import sys
        from io import StringIO
        import ufal.udpipe
        import pandas as pd
        from ufal.udpipe import Model, Pipeline, ProcessingError
        nl_model = Model.load("/Users/swa/Downloads/dutch-ud-2.1-20180111.udpipe")
        nl_pipeline = Pipeline(nl_model, "generic_tokenizer", Pipeline.DEFAULT, Pipeline.DEFAULT, "")
        en_model = Model.load("/Users/swa/Downloads/english-ud-2.1-20180111.udpipe")
        en_pipeline = Pipeline(en_model, "generic_tokenizer", Pipeline.DEFAULT, Pipeline.DEFAULT, "")
        def process(text, lang = "en"):
            error = ProcessingError()
            if lang == "en":
                processed = en_pipeline.process(text, error)
            else:
                processed = nl_pipeline.process(text, error)
            if error.occurred():
                sys.stderr.write("An error occurred when running run_udpipe: ")
                sys.stderr.write(error.message)
                sys.stderr.write("\n")
            sio = StringIO(processed)
            df = pd.read_csv(sio, sep="\t", skiprows=3)
            return df


Note that the accuracy of Dutch is not much above 60% as shown [here](http://www.bnosac.be/index.php/blog/75-a-comparison-between-spacy-and-udpipe-for-natural-language-processing-for-r-users) but as the world revolves around AI and NLP this figure will increase in the future.


## Documentation

The process is [a standard Sphinx setup](https://docs.readthedocs.io/en/latest/getting_started.html) which in essence consists of install Sphinx

        pip install sphinx sphinx-autobuild
        
creating a `docs` directory wherein you run

        sphinx-quickstart
        
which guides you through a setup. With the existing directory you only need to call

        make html
        
and you're done. The `docs/sources/index.rst` defines the content of the documentation and the `docs/source/conf.py` defines the context and general behavior.

The code is well documented and should help you to achieve whatever you're after. The unit tests also give help.

## Unit tests

Simply run 
        
        nosetests .

in the nalu directory to run all tests. If `nose` is not installed use

        pip install nose
        
See the [nose documentation](http://nose.readthedocs.io/en/latest/) if necessary.                                         

