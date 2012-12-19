from swanalyzer.sparql_analyzer import SPARQLAnalyzer

print 'Creating analyzer'
sparql_analyzer = SPARQLAnalyzer('http://helheim.deusto.es:8894/sparql', 'turismo', 'user=ckanuser password=pass host=localhost dbname=rdfstore', None, False)

print 'Opening connection'
sparql_analyzer.open()

print 'Loading graph'
sparql_analyzer.load_graph()

print 'Classes: ', len(sparql_analyzer.get_classes())

for c in sparql_analyzer.get_classes():
	print c[0]

print 'Closing connection'
sparql_analyzer.close()
