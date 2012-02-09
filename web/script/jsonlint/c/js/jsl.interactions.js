/*jslint white: true, devel: true, onevar: true, browser: true, undef: true, nomen: true, regexp: true, plusplus: false, bitwise: true, newcap: true, maxerr: 50, indent: 4 */
var jsl = typeof jsl === 'undefined' ? {} : jsl;

/**
 * Helper Function for Caret positioning
 * Gratefully borrowed from the Masked Input Plugin by Josh Bush
 * http://digitalbush.com/projects/masked-input-plugin
**/
$.fn.caret = function (begin, end) { 
    if (this.length === 0) {
        return;
    }
    if (typeof begin === 'number') {
        end = (typeof end === 'number') ? end : begin;  
        return this.each(function () {
        	try {
	            if (this.setSelectionRange) {
	                this.focus();
	                this.setSelectionRange(begin, end);
	            } else if (this.createTextRange) {
	                var range = this.createTextRange();
	                range.collapse(true);
	                range.moveEnd('character', end);
	                range.moveStart('character', begin);
	                range.select();
	            }
            } catch(ex) {}
        });
    } else {
    	try {
	        if (this[0].setSelectionRange) {
	            begin = this[0].selectionStart;
	            end   = this[0].selectionEnd;
	        } else if (document.selection && document.selection.createRange) {
	            var range = document.selection.createRange();
	            begin = -range.duplicate().moveStart('character', -100000);
	            end   = begin + range.text.length;
	        }
	        return {"begin": begin, "end": end};
    	} catch(ex) {}
	}       
};


/**
 * jsl.interactions - provides support for interactions within JSON Lint.
 *
**/
jsl.interactions = (function () {
    //var reformat;
    //var compress;
	//var reformatParam;


    /******* UTILITY METHODS *******/

    /**
     * Get the Nth position of a character in a string
     * @searchStr the string to search through
     * @char the character to find
     * @pos int the nth character to find, 1 based.
     *
     * @return int the position of the character found
    **/
    function getNthPos(searchStr, char, pos) {
        var i,
            charCount = 0,
            strArr = searchStr.split(char);

        if (pos === 0) {
            return 0;
        }

        for (i = 0; i < pos; i++) {
            if (i >= strArr.length) {
                return -1;
            }

            // +1 because we split out some characters
            charCount += strArr[i].length + char.length;
        }

        return charCount;
    }

    /**
     * Get a URL parameter from the current windows URL.
     * Courtesy Paul Oppenheim: http://stackoverflow.com/questions/1403888/get-url-parameter-with-jquery
     * @param name the parameter to retrieve
     * @return string the url parameter's value, if any
    **/
    //function getURLParameter(name) {
    //    param = (new RegExp(name + '=' + '(.+?)(&|$)').exec(location.search) || ['', null])[1];
    //    if (param) {
    //        return decodeURIComponent(param);
    //    } else {
    //        return null;
    //    }
    //}

    /******* INTERACTION METHODS *******/

    /**
     * Validate the JSON we've been given, displaying an error or success message.
     * @return void
    **/
    function validate($json_input, $results_div, reformat, compress) {
        var lineNum,
            lineMatches,
            lineStart,
            lineEnd,
            jsonVal,
            result;
            
        jsonVal = $json_input.val();

        try {
            result = jsl.parser.parse(jsonVal);

            if (result) {
                happy($json_input, $results_div, 'Valid JSON');

                if (reformat) {
                    $json_input.val(JSON.stringify(JSON.parse(jsonVal), null, "    "));
                }

                if (compress) {
                    $json_input.val(JSON.stringify(JSON.parse(jsonVal), null, ""));
                }
            } else {
                alert("An unknown error occurred.");
            }
        } catch (parseException) {

            /** 
             * If we failed to validate, run our manual formatter and then re-validate so that we
             * can get a better line number. On a successful validate, we don't want to run our
             * manual formatter because the automatic one is faster and probably more reliable.
            **/
            try {
                if (reformat) {
                    jsonVal = jsl.format.formatJson($json_input.val());
                    $('#json_input').val(jsonVal);
                    result = jsl.parser.parse($json_input.val());
                }
            } catch(e) {
                parseException = e;
            }

            lineMatches = parseException.message.match(/line ([0-9]*)/);
            if (lineMatches && typeof lineMatches === "object" && lineMatches.length > 1) {
                lineNum = parseInt(lineMatches[1], 10);

                if (lineNum === 1) {
                    lineStart = 0;
                } else {
                    lineStart = getNthPos(jsonVal, "\n", lineNum - 1);
                }

                lineEnd = jsonVal.indexOf("\n", lineStart);
                if (lineEnd < 0) {
                    lineEnd = jsonVal.length;
                }

                $json_input.focus().caret(lineStart, lineEnd);
            }
            
            sad($json_input, $results_div, parseException.message);
        }
    }

	function happy($json_input, $results_div, msg) {
        $results_div.text(msg);
        $results_div.removeClass('ui-state-error').addClass('ui-state-happy');
        $json_input.removeClass('redBorder').addClass('greenBorder');
	}
	function sad($json_input, $results_div, msg) {
        $results_div.text(msg);
        $results_div.removeClass('ui-state-happy').addClass('ui-state-error');
        $json_input.removeClass('greenBorder').addClass('redBorder');
	}
    /**
     * Initialize
     *
     * @return void
    **/
    function init($btn, $json_input, $results_div, reformat, compress) {
    	$btn.button({ icons: { primary: "ui-icon-check"} });
        $btn.click(function () {
            validate($json_input, $results_div, reformat, compress);
            return false;
        });
		
       $json_input.keyup(function () {
            $(this).removeClass('greenBorder').removeClass('redBorder');
        });
    }

    return {
        'init': init,
        'validate': validate
    };
}());

//this is the same as $(document).ready(function () ...
//so it runs when the page is loaded.
//if we eventually need to make these args different on a different page, 
//take this out and init the interactions manually.
//$(function () {
//    jsl.interactions.init(true, false);    
//});
