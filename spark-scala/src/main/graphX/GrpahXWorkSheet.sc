import org.apache.spark._
import org.apache.spark.graphx._
import org.apache.spark.graphx.util.GraphGenerators
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession
// To make some of the examples work we will also need RDD


val spark = SparkSession.builder
  .master("local")
  .appName("scalaWorksheet")
  .getOrCreate()
val sc: SparkContext = spark.sparkContext
val users =
  sc.parallelize(Array((3L, ("rxin", "student")), (7L, ("jgonzal", "postdoc")),
    (5L, ("franklin", "prof")), (2L, ("istoica", "prof"))))

// Create an RDD for edges
val relationships =
  sc.parallelize(Array(Edge(3L, 7L, "collab"),    Edge(5L, 3L, "advisor"),
    Edge(2L, 5L, "colleague"), Edge(5L, 7L, "pi")))
// Define a default user in case there are relationship with missing user
val defaultUser = ("John Doe", "Missing")
// Build the initial Graph
val graph: Graph[(String, String), String] = Graph(users, relationships, defaultUser)

val firstVertex =  graph.vertices.take(1)

val firstEdge = graph.edges.take(1)
val inDegrees = graph.inDegrees.foreach(println)

val triplet = graph.triplets.first()


val facts: RDD[String] =
  graph.triplets.map(triplet =>
    //triplet.srcAttr._1 + " is the " + triplet.attr + " of " + triplet.dstAttr._1)
    triplet.toString())
facts.collect.foreach(println(_))


val connected: Graph[VertexId, String] = graph.connectedComponents()


val ccGraph: Graph[VertexId, String] = graph.mapVertices { case (vid, x) => vid }


val pageR = graph.pageRank(0.001).vertices
pageR.foreach(println)



val graphGen: Graph[Double, Int] =
  GraphGenerators.logNormalGraph(sc, numVertices = 20).mapVertices( (id, _) => id.toDouble )

val olderFollowers: VertexRDD[(Int, Double)] = graphGen.aggregateMessages[(Int, Double)](
  triplet => { // Map Function
    if (triplet.srcAttr > triplet.dstAttr) {
      // Send message to destination vertex containing counter and age
      triplet.sendToDst((1, triplet.srcAttr))
    }
  },
  // Add counter and age
  (a, b) => (a._1 + b._1, a._2 + b._2) // Reduce Function
)

// Divide total age by number of older followers to get average age of older followers
val avgAgeOfOlderFollowers: VertexRDD[Double] =
  olderFollowers.mapValues( (id, value) =>
    value match { case (count, totalAge) => totalAge / count } )
// Display the results
avgAgeOfOlderFollowers.collect.foreach(println(_))

val sourceId: VertexId = 42 // The ultimate source

val initialGraph = graphGen.mapVertices((id, _) =>
  if (id == sourceId) 0.0 else Double.PositiveInfinity)

graph.outerJoinVertices()


val sssp = initialGraph.pregel(Double.PositiveInfinity)(
  (id, dist, newDist) => math.min(dist, newDist), // Vertex Program
  triplet => {  // Send Message
    if (triplet.srcAttr + triplet.attr < triplet.dstAttr) {
      Iterator((triplet.dstId, triplet.srcAttr + triplet.attr))
    } else {
      Iterator.empty
    }
  },
  (a, b) => math.min(a, b) // Merge Message
)
println(sssp.vertices.collect.mkString("\n"))

val sourceId1: VertexId = 42 // The ultimate source


//val gens: RDD[String] = graphGen.triplets.map(triplet =>
//  //triplet.srcAttr._1 + " is the " + triplet.attr + " of " + triplet.dstAttr._1)
//  triplet.toString())
//
//println(gens.first())
//
//
//graph
//
//
//gens.collect.foreach(println(_))






