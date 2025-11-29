import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.net.URI;
import com.google.gson.Gson;

public class HelloWorld {

    public static void main(String[] args) {
        System.out.println("Hello, World!");

        for(int i = 0; i < 10; i++ ){
            for(int j = 0; j < 15; j++){
                for (int k = 0; k < 20; k++){
                    System.out.println(i + j + k);
                }
            }
        }

    }
}

public void helper() {
    System.out.println("I'm a helper");
}
