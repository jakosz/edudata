<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"><html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title>
			Weryfikator zbiorów danych ilościowych
		</title>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
		<link href="style.css" rel="stylesheet" type="text/css"/>
		<script type="text/javascript" src="jquery.js"></script>
		<script type="text/javascript" src="skrypty.js"></script>
		<script type="text/javascript">
			var ID='1352303877.4360621849959370';
		</script>
	</head>
	<body>
		<div style="text-align: center; margin: 20px;">
			<a href="codebook_faq.pdf">Codebook - często zadawane pytania</a>
		</div>
		<form action="odbierz.php" method="post" enctype="multipart/form-data" target="rezultat">
			plik danych: <input type="file" name="plikDanych"/>
			<br/>
			codebook: <input type="file" name="plikCodebook"/>
			<input type="submit" value="skrypt importu do SPSS" name="importSPSS"/>
			<input type="submit" value="skrypt importu do Stata" name="importStata"/>
			<input type="button" value="funkcja importu do R" onclick="window.open('wczytaj_dane.r', '');"/>
			<input type="hidden" name="MAX_FILE_SIZE" value="100000000"/>
			<input type="hidden" name="ID" value="1352303877.4360621849959370"/>
			<input type="hidden" name="nazwaBadania" value=""/>
			<br/>
			Maksymalna liczba błędów: 
			<input type="text" value="10000" name="max_bledow" style="width: 80px;"/>
			<br/>
			<input type="submit" value="sprawdź" name="sprawdz" onclick="$('postep tr.dane td').html('');"/>
			<input type="button" value="przekaż" onclick="przekaz();"/>
			<input type="submit" value="lista przekazanych zbiorów" name="listaPrzekazanych"/>
		</form>
		<div id="postep">
		</div>
		<iframe src="" name="rezultat" id="rezultat" frameborder="0" width="100%"></iframe>
	</body>
</html>
