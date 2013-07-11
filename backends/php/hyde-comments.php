<?php
$debug = 0;
$from_address = "webmaster@noreply.net";
$to_address = "yourmail@yourdomain.net";
$subject = "[Hyde comments] New comment received";

$debug and ini_set('display_errors', 'On');
$debug and error_reporting(E_ALL | E_STRICT);

function badRequest($message = "Error 400: Bad Request")
{
	header("HTTP/1.1 400 Bad Request");
	echo $message;
	exit();
}



if (! isset($_SERVER['HTTP_REFERER'])) badRequest();
$referrer = $_SERVER['HTTP_REFERER'];

if ($debug)
{
	echo '<pre>';
	var_dump($_POST);
}

class MissingField extends Exception
{
	function __construct($field)
	{
		parent::__construct("Missing field '$field'");
	}
};

/// Safely retrieves post data or throws unless a default value is provided
function post($field, $default=Null)
{
	if (!isset($_POST[$field]))
	{
		if (!is_null($default)) return $default;
		throw new MissingField($field);
	}
	if (empty($_POST[$field]) and !is_null($default))
		return $default;
	return $_POST[$field];
}

function sluggify($string)
{
	$result = preg_replace('/[^A-Za-z0-9-]+/', '-', $string); // Weird into '-'
	$result = preg_replace('/--*/', '-', $result); // Collapse multiple '-'
	$result = preg_replace('/-$/', '', $result); // Remove '-' at ending
	$result = preg_replace('/^-/', '', $result); // Remove '-' at begining
	return $result;
}

date_default_timezone_set("UTC");
$time = date("Y-m-d H:i:s");
$slug_time = date("Ymd-His");
$title_excerpt_size=20;
$random_hash = md5(rand());

try
{
	$comment = post('comment');
	$title_excerpt = substr($comment, 0, strpos(wordwrap($comment, $title_excerpt_size), "\n"));
	$thread = post('thread');
	$inreplyto = post('inreplyto');
	$author = post('name');
	$authoremail = post('email');
	// Optional params
	$authoruri = post('website', "");
	$title = post('title', $title_excerpt);
}
catch (MissingField $e)
{
	badRequest($e->getMessage());
}
$short_hash = substr($random_hash,-6);
$id = sluggify("$thread-$slug_time-$short_hash-$title");

$comment_file = <<<EOF
---
id: '$id'
thread: '$thread'
inreplyto: '$inreplyto'
title: '$title'
published: !!timestamp '$time'
updated: !!timestamp '$time'
author: "$author"
authoruri: $authoruri
authoremail: $authoremail
---
$comment
EOF;

if ($debug)
{
	echo $comment_file;
	echo '</pre>';
}

$message = <<<EOF
--Multipart-boundary-$random_hash
Content-Type: text/plain; charset="utf-8

Someone commented you post at:
$referrer

To incorporate such comment into your blog,
save the attached file into the content folder
and regenerate the blog with Hyde.

Author: $author
Email: $authoremail
Website: $authoruri
Title: $title
Content:
------------------
$comment
------------------

Sincerely,
  your PHP backend for the Hyde static comments plugin.

--Multipart-boundary-$random_hash
Content-Type: text/yaml; name="$id.comment"; charset="utf-8"
Content-Disposition: attachment

$comment_file
EOF;

if (! $debug )
{

	$ok = @mail(
		$to_address,
		$subject,
		$message,
		join("\r\n",array(
			"From: $from_address",
			"Reply-To: $from_address",
			"Content-Type: multipart/mixed; boundary=\"Multipart-boundary-$random_hash\"" 
			))
		);
	if ($ok)
	{
		echo <<<EOF
<html>
<head> <meta charset="utf-8" /> </head>
<body>
<p>Thanks. Your comment was properly submitted.
</p><p>
Do not expect the comments to appear immediately in the post
as they have to wait for author's moderation.</p>
<p><a href='$referrer'>Back to the post</a></p>
</body>
</html>
EOF;

	}
	else
	{
		echo <<<EOF
<html>
<head> <meta charset="utf-8" /> </head>
<body>
<p>We are sorry. There was a problem submiting your comment.
</p><p>
Below you have the content of your comment so that you can copy it and submit it later.</p>
<pre>
Title: $title
------------------
$comment
------------------
</pre>
<p><a href='$referrer'>Back to the post</a></p>
</body>
</html>
EOF;
	}
}

?>
