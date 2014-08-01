(function ($) {

	var b64array = "ABCDEFGHIJKLMNOP" +
           "QRSTUVWXYZabcdef" +
           "ghijklmnopqrstuv" +
           "wxyz0123456789+/" +
           "=";

	function decodeBase64(data) {
		// from http://decodebase64.com/
		var output = "";
		var hex = "";
		var chr1, chr2, chr3 = "";
		var enc1, enc2, enc3, enc4 = "";
		var i = 0;

		data = data.replace(/[^A-Za-z0-9\+\/\=]/g, "");

		do {
			enc1 = b64array.indexOf(data.charAt(i++));
			enc2 = b64array.indexOf(data.charAt(i++));
			enc3 = b64array.indexOf(data.charAt(i++));
			enc4 = b64array.indexOf(data.charAt(i++));

			chr1 = (enc1 << 2) | (enc2 >> 4);
			chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
			chr3 = ((enc3 & 3) << 6) | enc4;

			output = output + String.fromCharCode(chr1);

			if (enc3 != 64) {
				output = output + String.fromCharCode(chr2);
			}
			if (enc4 != 64) {
				output = output + String.fromCharCode(chr3);
			}

			chr1 = chr2 = chr3 = "";
			enc1 = enc2 = enc3 = enc4 = "";

		} while (i < data.length);

		return output;
	}

	function convertMarkdown(markdownToConvert) {
		return marked(markdownToConvert);
	}

	$.fn.readme = function (options) {
		var deferred = new $.Deferred();
		var self = this;
		var owner = options.owner;
		var repo = options.repo;
		$.get('https://api.github.com/repos/' + owner + '/' + repo + '/readme', function (response) {
			var markdownToConvert = decodeBase64(response.content);
			var html = convertMarkdown(markdownToConvert);
			$(self).html(html);
			deferred.resolve();
		});
		return deferred.promise();
	};

})(jQuery);