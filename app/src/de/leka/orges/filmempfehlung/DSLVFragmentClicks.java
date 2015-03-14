package de.leka.orges.filmempfehlung;

import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;
import android.os.Bundle;
import android.widget.Toast;
import android.net.Uri;
import android.content.Intent;

public class DSLVFragmentClicks extends DSLVFragment {

    public static DSLVFragmentClicks newInstance(int headers, int footers) {
        DSLVFragmentClicks f = new DSLVFragmentClicks();

        Bundle args = new Bundle();
        args.putInt("headers", headers);
        args.putInt("footers", footers);
        f.setArguments(args);

        return f;
    }


    @Override
    public void onActivityCreated(Bundle savedState) {
        super.onActivityCreated(savedState);

        ListView lv = getListView();
        lv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> arg0, View arg1, int arg2,
                    long arg3) {
                //String message = String.format("Clicked item %d", arg2);
                //Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
                String url = tidToUrl.get(array[ordered.get(arg2)]);
                Uri uriUrl = Uri.parse(url);
                Intent launchBrowser = new Intent(Intent.ACTION_VIEW, uriUrl);
                startActivity(launchBrowser);
                
            }
        });
        lv.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
            @Override
            public boolean onItemLongClick(AdapterView<?> arg0, View arg1, int arg2,
                    long arg3) {
                String message = String.format("Long-clicked %s", tidToTitle.get(array[ordered.get(arg2)]));
                Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
                return true;
            }
        });
    }
}
