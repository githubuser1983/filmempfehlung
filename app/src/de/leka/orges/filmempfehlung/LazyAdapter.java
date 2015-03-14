package de.leka.orges.filmempfehlung;

import java.util.ArrayList;
import java.util.HashMap;

import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

public class LazyAdapter extends BaseAdapter {
    
    private Activity activity;
    private ArrayList<HashMap<String, String>> data;
    private static LayoutInflater inflater=null;
    public ImageLoader imageLoader; 
    
    public LazyAdapter(Activity a, ArrayList<HashMap<String, String>> d) {
        activity = a;
        data=d;
        inflater = (LayoutInflater)activity.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        imageLoader=new ImageLoader(activity.getApplicationContext());
    }

    public int getCount() {
        return data.size();
    }

    public Object getItem(int position) {
        return position;
    }

    public long getItemId(int position) {
        return position;
    }
    
    public View getView(int position, View convertView, ViewGroup parent) {
        View vi=convertView;
        if(convertView==null)
            vi = inflater.inflate(R.layout.simplerow, null);

        TextView title = (TextView)vi.findViewById(R.id.title); // title
        TextView genres = (TextView)vi.findViewById(R.id.genres); // genres
        
        ImageView thumb_image=(ImageView)vi.findViewById(R.id.movie_icon); // thumb image
        
        HashMap<String, String> movie = new HashMap<String, String>();
        movie = data.get(position);
        
        // Setting all values in listview
        title.setText(movie.get(ListViewActivity.KEY_TITLE));
        genres.setText(movie.get(ListViewActivity.KEY_GENRES));
        
        imageLoader.DisplayImage(movie.get(ListViewActivity.KEY_POSTER_PATH_URL), thumb_image);
        return vi;
    }
}