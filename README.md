<h1>Presentation de la structure du projet</h1>

Le projet se présente sous forme de notebook python, developpé pour un cours de 5IF à l'INSA de Lyon.

L'équipe est composée de :
<ul>
	<li>Nathan  Arsac</li>
	<li>Arij Daif</li>
	<li>Arnaud  Dupeyrat</li>
	<li>Jacques Folléas</li>
	<li>Mathis   Hammel</li>
	<li>Riham Razoki</li>
</ul>


<h2> But du projet </h2>

Le but du projet est de construire un outil de référencement permettant de trouver les articles les plus pertinent en fonction d'une requete de l'utilisateur.
Le but étant de comprendre les principes du référencement en manipulant en autre le concept de TF-IDF, les différents implementations de l'algorithme de fagins et les postings listes.

<h2> Structure du projet </h2>

Le projet se structure en différents fichier python représentant chacun une étape de la construction de l'outil de referencement regrouper dans le dossier <b> ./src </b>: 

<ul>
	 <li><b>indexFile.ipynb</b> => notebook permettant d'éxecuter les différents fichier</li>
	 	
		<li><b>util_index.py</b> => permettant d'effectuer le preprocessing des données, tokenization, stemming, stop-word removal permettant de construire les posting list plus petite.</li>
		
	<li><b>util_posting.py</b> => TODO r</li>
		
		<li><b>encoded_posting.py</b> => TODO</li>
		
	<li><b>graph.py</b> => contenant le code pour la construction et l'affichage des graphs de performance</li>
		
	<li><b>naive.py</b> => contenant l'implementation naive pour calculer les meilleurs k meilleurs articles</li>
	
	<li><b>faginsNaive.py</b> => contenant l'implementation de fagins naive pour calculer les meilleurs k meilleurs articles </li>
		
	<li><b>fagins.py</b> => contenant l'implementation de fagins threshold pour calculer les meilleurs k meilleurs articles </li>
</ul>