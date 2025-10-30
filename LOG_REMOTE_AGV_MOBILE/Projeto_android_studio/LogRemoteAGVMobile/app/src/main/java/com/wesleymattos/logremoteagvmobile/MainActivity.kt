// MainActivity.kt
package com.seuapp.firenew

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.google.firebase.database.*
import kotlinx.android.synthetic.main.activity_main.*

class MainActivity : AppCompatActivity() {

    private lateinit var database: DatabaseReference

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        database = FirebaseDatabase.getInstance().reference

        // Exemplo: Lendo os dados em tempo real de sensores/temperatura e sensores/umidade
        database.child("sensores/temperatura").addValueEventListener(object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val temp = snapshot.getValue(String::class.java)
                textTemperatura.text = "Temperatura: $temp °C"
            }

            override fun onCancelled(error: DatabaseError) {
                textTemperatura.text = "Erro na leitura"
            }
        })

        database.child("sensores/umidade").addValueEventListener(object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val umidade = snapshot.getValue(String::class.java)
                textUmidade.text = "Umidade: $umidade %"
            }

            override fun onCancelled(error: DatabaseError) {
                textUmidade.text = "Erro na leitura"
            }
        })
    }
}
