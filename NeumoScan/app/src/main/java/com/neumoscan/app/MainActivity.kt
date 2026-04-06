package com.neumoscan.app

import androidx.compose.foundation.layout.Box
import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.icu.text.SimpleDateFormat
import android.net.Uri
import android.os.Bundle
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import android.os.Environment
import android.provider.MediaStore
import android.widget.ImageView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import com.neumoscan.app.ui.theme.NeumoScanTheme
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.Date
import java.util.Locale
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.Response
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import org.json.JSONObject
import android.app.AlertDialog
import android.content.Context
import android.os.Handler


class MainActivity : ComponentActivity() {
    private companion object {
        private const val REQUEST_IMAGE_CAPTURE = 1
        private const val PERMISSION_REQUEST_CODE = 1001
    }

    private var currentPhotoPath: String? = null
    private lateinit var imageView: ImageView

    private val apiDiagnosis: MutableState<String> = mutableStateOf("Waiting results...")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NeumoScanTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            verticalArrangement = Arrangement.Center,
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Greeting("William")
                            InfoMain()
                            Spacer(modifier = Modifier.height(16.dp))
                            TakePhotoButton(this@MainActivity)
                        }
                        if (currentPhotoPath != null) {
                            ShowPhoto(currentPhotoPath!!)
                        }
                    }
                }
            }
        }
        checkAndRequestPermissions()
    }

    private fun checkAndRequestPermissions() {
        val permissionsToRequest = mutableListOf<String>()
        val cameraPermission = Manifest.permission.CAMERA
        val storagePermission = Manifest.permission.WRITE_EXTERNAL_STORAGE

        // Verifica el permiso de la cámara
        if (!isPermissionGranted(cameraPermission)) {
            permissionsToRequest.add(cameraPermission)
        }

        // Verifica el permiso de almacenamiento
        if (!isPermissionGranted(storagePermission)) {
            permissionsToRequest.add(storagePermission)
        }

        // Solicita los permisos necesarios
        if (permissionsToRequest.isNotEmpty()) {
            requestPermissions(
                permissionsToRequest.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        } else {
            // Todos los permisos ya están otorgados, puedes proceder con la captura de la imagen
        }
    }


    private fun isPermissionGranted(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            permission
        ) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        if (requestCode == PERMISSION_REQUEST_CODE) {
            var allPermissionsGranted = true
            for (result in grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allPermissionsGranted = false
                    break
                }
            }
            if (allPermissionsGranted) {
                // Los permisos fueron otorgados, puedes proceder con la captura de la imagen
                captureImage()
            } else {
                // Al menos uno de los permisos no fue otorgado, puedes mostrar un mensaje de error o tomar alguna otra acción
                Toast.makeText(this, "Se requieren permisos de cámara", Toast.LENGTH_SHORT).show()
            }
        } else {
            super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        }
    }

    private fun captureImage() {
        val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        if (takePictureIntent.resolveActivity(packageManager) != null) {
            val photoFile: File? = try {
                createImageFile()
            } catch (ex: IOException) {
                // Maneja el error al crear el archivo
                ex.printStackTrace()
                null
            }
            // Continúa solo si el archivo se ha creado correctamente
            photoFile?.also {
                val photoURI: Uri = FileProvider.getUriForFile(
                    this,
                    "com.neumoscan.app.fileprovider",
                    it
                )
                // Guarda la ruta de la imagen para su posterior uso
                currentPhotoPath = photoFile.absolutePath
                // Configura la URI del archivo como extra en el intent de la cámara
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE)
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == Activity.RESULT_OK) {
            val photoFile = File(currentPhotoPath)
            if (photoFile.exists()) {
                apiDiagnosis.value = "Waiting results...";
                sendImageToWebService(photoFile)
                setContent {
                    showPopup(this);
                    DefaultPreview(photoFile.absolutePath);
                }
            }
        }
    }

    private fun saveImageToGallery(imageBitmap: Bitmap) {
        val timeStamp: String =
            SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val imageFileName = "JPEG_${timeStamp}.jpg"
        val storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)

        val imageFile = File(storageDir, imageFileName)
        val outputStream = FileOutputStream(imageFile)
        imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream)
        outputStream.flush()
        outputStream.close()

        // Añade la foto a la galería
        val mediaScanIntent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
        val contentUri = Uri.fromFile(imageFile)
        mediaScanIntent.data = contentUri
        sendBroadcast(mediaScanIntent)
    }


    @Composable
    fun Greeting(name: String) {
        Text(
            text = "Hello $name!",
            modifier = Modifier.padding(16.dp),
            color = Color.White,
            fontWeight = FontWeight.Bold
        )
    }

    @Composable
    fun InfoMain() {
        Text(
            text = "Take a picture of a chest x-ray to analyze whether or not you have pneumonia.",
            modifier = Modifier.padding(16.dp),
            color = Color.White,
            textAlign = TextAlign.Center
        )
    }

    @Throws(IOException::class)
    private fun createImageFile(): File {
        // Crea un nombre único para el archivo de imagen
        val timeStamp: String =
            SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir: File? = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile(
            "JPEG_${timeStamp}_", /* prefijo del archivo */
            ".jpg", /* extensión del archivo */
            storageDir /* directorio de almacenamiento */
        ).apply {
            // Guarda la ruta del archivo
            currentPhotoPath = absolutePath
        }
    }

    private fun dispatchTakePictureIntent() {
        captureImage()
    }

    private fun sendImageToWebService(photoFile: File) {
        val client = OkHttpClient()

        // Construye el cuerpo de la solicitud multipart/form-data
        val requestBody = MultipartBody.Builder().setType(MultipartBody.FORM)
            .addFormDataPart(
                "imagen",
                photoFile.name,
                photoFile.asRequestBody("image/jpeg".toMediaType())
            )
            .build()

        // Construye la solicitud POST con el cuerpo y la URL del servicio web
        val apiUrl = getString(R.string.api_base_url) + "/neumoscan"
        val request = Request.Builder()
            .url(apiUrl)
            .post(requestBody)
            .build()

        // Ejecuta la operación de red en un hilo separado
        val thread = Thread {
            try {
                val response: Response = client.newCall(request).execute()
                // Procesa la respuesta del servicio web aquí
                if (response.isSuccessful) {
                    // La solicitud fue exitosa
                    val responseBody = response.body?.string()
                    showImageResponse(responseBody.toString())
                } else {
                    // La solicitud no fue exitosa
                    // Maneja el error de la solicitud
                }
            } catch (e: IOException) {
                e.printStackTrace()
                // Maneja la excepción de la solicitud
            }
        }
        thread.start()
    }


    @Composable
    fun TakePhotoButton(activity: ComponentActivity) {
        Button(
            onClick = { dispatchTakePictureIntent() },
            modifier = Modifier.padding(16.dp)
        ) {
            Text(text = "Take Photo")
        }
    }

    @Preview(showBackground = true)
    @Composable
    fun DefaultPreview(path: String) {
        NeumoScanTheme {
            if (path != null) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Top,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    DiagnosisText(apiDiagnosis.value)
                    ShowPhoto(path!!)
                    TakePhotoButton(activity = ComponentActivity())
                }
            }
        }
    }

    @Composable
    fun DiagnosisText(diagnosis: String) {
        val (displayText, color) = when {
            diagnosis.contains("NORMAL", ignoreCase = true) ->
                Pair("NORMAL", Color(0xFF2E7D32))       // verde oscuro
            diagnosis.contains("BACTERIAL", ignoreCase = true) ->
                Pair("BACTERIAL\nPNEUMONIA", Color(0xFFB71C1C))  // rojo oscuro
            diagnosis.contains("VIRAL", ignoreCase = true) ->
                Pair("VIRAL\nPNEUMONIA", Color(0xFFE65100))      // naranja oscuro
            diagnosis.contains("INCONCLUSIVE", ignoreCase = true) ->
                Pair("INCONCLUSIVE\nLow confidence", Color(0xFF37474F)) // gris azulado
            else ->
                Pair(diagnosis, Color.DarkGray)
        }
        Text(
            text = displayText,
            modifier = Modifier.padding(16.dp),
            color = color,
            textAlign = TextAlign.Center,
            fontSize = 36.sp,
            fontWeight = FontWeight.ExtraBold
        )
    }

    private fun updateDiagnosis(diagnosis: String) {
        // Actualiza el valor del MutableState con la respuesta del web service
        apiDiagnosis.value = diagnosis
    }

    private fun showImageResponse(response: String) {
        runOnUiThread {
            try {
                val jsonResponse = JSONObject(response)
                val prediction = jsonResponse.getString("prediction")
                updateDiagnosis(prediction)
            } catch (e: Exception) {
                e.printStackTrace()
                // Manejar cualquier error al analizar el JSON o al obtener el campo "prediction"
            }
        }
    }

    fun showPopup(context: Context) {
        val diagnosis = apiDiagnosis.value
        val isResolved = diagnosis.contains("NORMAL", ignoreCase = true)
                || diagnosis.contains("BACTERIAL", ignoreCase = true)
                || diagnosis.contains("VIRAL", ignoreCase = true)
                || diagnosis.contains("INCONCLUSIVE", ignoreCase = true)

        val builder = AlertDialog.Builder(context)
        builder.setTitle("NeumoScan Diagnosis")
        builder.setMessage(diagnosis)

        if (isResolved) {
            builder.setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            builder.create().show()
        } else {
            // Aún esperando respuesta — auto-dismiss a los 3 segundos
            val dialog = builder.create()
            dialog.show()
            Handler().postDelayed({ dialog.dismiss() }, 3000)
        }
    }


    @Composable
    fun ShowPhoto(photoPath: String) {
        val imageBitmap = loadImageBitmap(photoPath)
        imageBitmap?.let {
            Image(
                painter = BitmapPainter(it),
                contentDescription = null,
                modifier = Modifier.padding(16.dp)
            )
        }
    }

    private fun loadImageBitmap(photoPath: String): ImageBitmap? {
        val photoFile = File(photoPath)
        return if (photoFile.exists()) {
            BitmapFactory.decodeFile(photoFile.absolutePath)?.asImageBitmap()
        } else {
            null
        }
    }
}

