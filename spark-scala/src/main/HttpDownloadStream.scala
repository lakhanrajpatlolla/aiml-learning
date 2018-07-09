package client.HttpUtils

import java.io.{File, FileOutputStream, InputStream, OutputStream}

/**
  * Created by lpatlolla on 3/21/17.
  */

object DownloadContentUsingStream extends Logging {

  def downloadFile(url: String, authToken: String, outputFile: String) = {
    val inputStream = getUrlInputStream(url , authToken)
    val file = new File(outputFile)
    logger.info("Writing file: " + file.getAbsolutePath)
    if(! file.getParentFile.exists()) {
      file.getParentFile.mkdirs()
    }
    val outputStream: FileOutputStream = new FileOutputStream(file)
    copyStream(inputStream, outputStream)
    inputStream.close()
    outputStream.close()
  }

  def copyStream(input:InputStream, output:OutputStream) = {
    val buffer = new Array[Byte](1024)
    var n = input.read(buffer)
    while(n >= 0) {
      output.write(buffer, 0, n)
      n = input.read(buffer)
    }
    output.flush()
    output.close()
  }

  private def getUrlInputStream(url: String,
    authToken:String,
    connectTimeout: Int = HttpRestClient.ConnectionTimeout,
    readTimeout: Int = HttpRestClient.ReadTimeout,
    requestMethod: String = "GET") = {
    import java.net.{HttpURLConnection, URL}
    val u = new URL(url.replaceAll(" ", "%20"))
    val conn = u.openConnection.asInstanceOf[HttpURLConnection]
    HttpURLConnection.setFollowRedirects(false)
    conn.setConnectTimeout(connectTimeout)
    conn.setReadTimeout(readTimeout)
    conn.setRequestMethod(requestMethod)
    conn.setRequestProperty("X-Auth-Token", authToken)
    conn.connect
    conn.getInputStream
  }
}
